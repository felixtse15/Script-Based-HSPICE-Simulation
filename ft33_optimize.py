import os
import subprocess
import numpy as np
import re
import time

# File names and constants
SPICE_NETLIST = "ft33_nlistcopy.sp"
RUN_HSPICE = "/clear/apps/elec8/bin/hspice"
RUN_PARSE = "ft33_parse.py"
NUM_STAGES = 1    ####################### MUST BE ODD, CHANGE THIS TO RUN FOR DIFFERENT STAGES ############################
STEP_SIZE = 0.1
LEARNING_RATE = 0.01
INITIAL_SCALE = 2.5
MAX_ITERATIONS = 20


# Function to run simulation and parse all results
def sim_parse(stages):
    
    # Run Hspice, read the main parameters and all .alter blocks.
    hspice_cmd = [RUN_HSPICE, SPICE_NETLIST]
    subprocess.run(hspice_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Loop through the output files Hspice created (.mt0, .mt1, etc.) and parse each one.
    for n in range(stages + 1):
    
        # Hspice names the output based on the input file, e.g., mysample.mt0
        mt_filename = f"{SPICE_NETLIST.split('.')[0]}.mt{n}"
        output_filename = f"output{n}.txt"
        parse_cmd = ["python3", RUN_PARSE, mt_filename, output_filename, "delay", "energy_total"]
        subprocess.run(parse_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
      

# Function to get delay 
def get_metrics(output_filename):

    with open(output_filename) as out_f:
        lsfile = out_f.readlines()
        d = lsfile[1]
        
        # Split the strings (delay and energy) by comma, convert to float
        metrics = [float(x) for x in d.split(',')]
        
        # Convert seconds to picoseconds, joules to picojoules
        metrics = [x * 1e12 for x in metrics]     
    
    # Return list of two metrics
    return metrics 

 

        
# Get new size values with gradient descent
def new_s_values(past_size_values, current_delays, past_delays, step_size, learning_rate, stages):
       
    # Create an empty list to store the gradient components
    gradient = []
    
    # Loop for each stage to calculate the gradient
    for stage in range(stages):
    
        # Calculate the change in delay for the current stage
        delay_difference = current_delays[stage] - past_delays[stage]
        
        # Calculate the gradient component and add it to the list
        # Gradient = (change in delay) / (change in size)
        gradient_component = delay_difference / step_size
        gradient.append(gradient_component)
        
    # Create an empty list to store the new size values
    new_sizes = []
    
    # Loop for each stage to calculate the new size values
    for stage in range(stages):
        # Calculate the new size using the gradient descent formula
        # new_value = old_value - learning_rate * gradient
        new_s_value = past_size_values[stage] - learning_rate * gradient[stage]
        rounded_new_s_value = round(new_s_value, 2)
        new_sizes.append(rounded_new_s_value)
        
    return new_sizes




# Set new sizes and instantiate drivers 
def set_s(stages, original_sp_file, new_sp_file):
    
    # Do nothing if an invalid number of stages is requested
    if stages < 1:
        print("Error: Number of stages must be 1 or greater.")
        return

    # Read all lines from the original file
    with open(original_sp_file) as f:
        lines = f.readlines()

    # Create a new list to hold the modified file content
    new_lines = []

    # Loop through the original lines to build the new file
    for line in lines:
    
        # Skip appending first driver
        if "X_driver0 DIN node_measure" in line:
            continue
        
        
        new_lines.append(line)

        # --- Find insertion points and add the new lines ---

        # Add new size parameters after the DRIVER-PARAMS header
        if "**\tDRIVER-PARAMS\t**" in line:
            for stage in range(1, stages + 1):
                # The value is 4^(stage-1), e.g., S2=4, S3=16
                new_lines.append(f"+       S{stage} = {INITIAL_SCALE**(stage)}\n")

        # Add the new driver chain after the DRIVER-STAGES header
        if "**\tDRIVER-STAGES\t**" in line:
            # Handle the first stage (input is always DIN)
            # Output changes if part of a longer chain
            output_node1 = "node_measure" if stages == 0 else "node1"
            new_lines.append(f'X_driver0 DIN {output_node1} vdd vss inv Wp="wid_p" Wn="wid_n"\n')
            
            # Add intermediate stages (these only exist if stages > 2)
            for stage in range(1, stages):
                input_node = f"node{stage}"
                output_node = f"node{stage + 1}"
                new_lines.append(f'X_driver{stage} {input_node} {output_node} vdd vss inv Wp="S{stage}*wid_p" Wn="S{stage}*wid_n"\n')

            # Add the final stage (this only exists if stages >= 1)
            if stages >= 1:
                input_node = f"node{stages}"
                output_node = "node_measure"
                new_lines.append(f'X_driver{stages} {input_node} {output_node} vdd vss inv Wp="S{stages}*wid_p" Wn="S{stages}*wid_n"\n')
        
        # Add new .alter blocks after the first one
        if "* Use Alter command to simulate other cases" in line:
            for stage in range(1, stages + 1):
                new_lines.append(f".alter\n")
                new_lines.append(f".PARAM S{stage}={INITIAL_SCALE**(stage)}\n")

    # Write newly created list of lines to the output file
    with open(new_sp_file, 'w') as fcopy:
        for line in new_lines:
            fcopy.write(line)


# Function to change the .alter values in netlist
def change_dsize(filename, values_to_write, stages):

    with open(filename) as f:
        lines = f.readlines()
        
    # Loop for each stage and find its .alter line by name
    for stage in range(stages):
        for i in range(len(lines)):
        
            # Find the parameter name for the correct stage
            if f".PARAM S{stage + 1}=" in lines[i] and ".alter" in lines[i-1]:
            
                # Replace the line with the new value
                lines[i] = f".PARAM S{stage + 1}={values_to_write[stage]}\n"
                break 
            
    # Write the modified content back to the same file
    with open(filename, 'w') as fcopy:
        for line in lines:
            fcopy.write(line)

# Function to change the main .PARAM values 
def change_base_s_values(filename, new_base_values, stages):
    with open(filename) as f:
        lines = f.readlines()

    # Find start and end of main driver parameters block
    param_start_idx = -1
    param_end_idx = -1
    for i, line in enumerate(lines):
        if "**\tDRIVER-PARAMS\t**" in line:
            param_start_idx = i
        if "**\tEND-PARAMS\t**" in line:
            param_end_idx = i
            break
            
    if param_start_idx == -1:
        print("Error: Could not find DRIVER-PARAMS section.")
        return

    # Replace the size parameters within the specific block
    for stage in range(stages):
        for i in range(param_start_idx, param_end_idx):
            if f"S{stage + 1} =" in lines[i]:
                lines[i] = f"+       S{stage + 1} = {new_base_values[stage]}\n"
                break 
    
    with open(filename, 'w') as fcopy:
        for line in lines:
            fcopy.write(line)
  
################ M A I N ###################
# Initial Setup

print("--- Initial Setup ---")
with open("ft33_netlist.sp") as f_orig:
    lines = f_orig.readlines()

# Create a copy of the original netlist
with open(SPICE_NETLIST, 'w') as f_copy:
    for line in lines:
        f_copy.write(line)

# Create the multi-stage netlist with placeholder values
set_s(NUM_STAGES, SPICE_NETLIST, SPICE_NETLIST)

# Define and write the initial size values for first run
current_s_values = [round(INITIAL_SCALE**(n + 1), 2) for n in range(NUM_STAGES)]
print(f"Initial S-Values: {current_s_values}")
change_base_s_values(SPICE_NETLIST, current_s_values, NUM_STAGES)


# Optimization loop
final_delay = 0
for i in range(MAX_ITERATIONS):
    print(f"\n--- Starting Iteration {i+1}/{MAX_ITERATIONS} ---")
    
    # Set .alter params with wiggled values
    wiggled_values = []
    for j in range(NUM_STAGES):
        wiggled_value = round(current_s_values[j] + STEP_SIZE, 2)
        wiggled_values.append(wiggled_value)
    
    change_dsize(SPICE_NETLIST, wiggled_values, NUM_STAGES)
    
    # Run simulation, parse results
    sim_parse(NUM_STAGES)
    
    # Collect results
    base_delay = get_metrics("output0.txt")[0]
    energy = get_metrics("output0.txt")[1]
    
    perturbed_delays = []
    for n in range(1, NUM_STAGES + 1):
        delay = get_metrics(f"output{n}.txt")[0]
        perturbed_delays.append(delay)
    
    past_delays = [base_delay] * NUM_STAGES
    
    # Calculate next set of size values
    next_s_values = new_s_values(
        past_size_values=current_s_values,
        current_delays=perturbed_delays,
        past_delays=past_delays,
        step_size=STEP_SIZE,
        learning_rate=LEARNING_RATE,
        stages=NUM_STAGES
    )
    
    # Print results, prepare for next loop
    print(f"Delay: {base_delay:.2f}ps |Energy: {energy:.2f}pJ |Current Sizes: {current_s_values} -> New Sizes: {next_s_values}")
    
    if current_s_values == next_s_values:
        print("\nConvergence reached. Sizes are no longer changing.")
        break
        
    # New values become base for the next iteration
    current_s_values = next_s_values
    
    # Update main .PARAM block in the file for the next iteration's base delay
    change_base_s_values(SPICE_NETLIST, current_s_values, NUM_STAGES)

with open("ft33_nlistcopy.mt0") as f:
    lines = f.readlines()

# Final print statements
sim_parse(NUM_STAGES)    
base_delay = get_metrics("output0.txt")[0]
energy = get_metrics("output0.txt")[1]
print("\n--- Optimization Finished ---")
print(f"Final Optimized Sizes: {current_s_values}")
print(f"Optimized Delay: {base_delay:.2f}ps")
print(f"Energy: {energy:.2f}pJ")
