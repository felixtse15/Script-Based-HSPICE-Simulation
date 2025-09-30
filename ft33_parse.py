##############################################################################
# Fall 2025, ELEC 521, Lab 1.2                                               #
#                                                                            #
# Author:                                                                    #
# Felix Tse, MECE                                                            #
#                                                                            #
# Last edit:                                                                 #
# September 14th, 2025                                                       #
#                                                                            #
# Usage:                                                                     #
# python3 ft33_parse.py <input_filename> <output_filename> <var1> <var2>..") #
#                                                                            #
# Description:                                                               #
# This script parses a *.mt* file into an output text file, named            #
# "prelab.txt". The first line of prelab.txt contains the variables          #
# requested by the user in the order requested. The remaining lines          #
# are organized into columns that correspond to the data for each            #
# variable, in the same order requested, while each line represents          #
# the data for a single simulation iteration. The elements of each           #
# row are separated by commas, no spaces. The script also checks for         #
# a sufficient number of arguments (at least 1 variable must be              #
# requested) and ignores duplicates if duplicate variables are requested.    #
# It also replaces 'failed' keywords from HSPICE simulation with 'NaN'       #
# for MATLAB processing.                                                     #            
#                                                                            #
# Assumptions/Notes:                                                         #
# - Number of lines for variables = number of lines for simulation iteration #
#   data                                                                     #
# - input file may or may not end with '\n' character                        #
# - assume input file is always in current directory                         #
# - Ignore duplicate, incorrect, or nonexistent variable calls               # 
#                                                                            #
##############################################################################

import sys

# Check that there are sufficient number of arguments
if len(sys.argv) < 4:
    print("Error: Please provide at least one variable name.")
    print("Usage: python3 ft33_parse.py <input_filename> <output_filename> <var1> <var2> ...")

# Get variables requested, ignore the script name argument and filenames
args = sys.argv[3:]

# Set filenames, assume in current directory
# Take input filename from sys.argv
file_in = sys.argv[1]
file_out = sys.argv[2]

# Create list to store output
output = []

with open(file_in) as f_i:
    
    # First, read file as list of strings
    lsfile = f_i.readlines()
    #DEBUGGING print(lsfile)

    # Remove first two elements and last element (ignore the comment, title, and the
    # ending '\n' character, if applicable)
    if lsfile[-1] == '\n':
        data = lsfile[2:-1]
    else:
        data = lsfile[2:]
    #DEBUGGING print(data)

    # Create a list that stores the variable names, remove whitespace characters and 
    # separate words by whitespace into a list
    # Final variable will always end on alter#, keep track of how many lines are used
    # to write variables = number of lines used for each simulation iteration
    varlist = []
    varlist = data[0].strip().split()
    num_lines = 1
    while(varlist[-1] != "alter#"):
            varlist += data[num_lines].strip().split()
            num_lines += 1
    #DEBUGGING print(varlist)
    #DEBUGGING print(num_lines)

    # Create a dictionary that maps each variable name to its column index
    var_to_idx = {var: idx for idx, var in enumerate(varlist)}
    #DEBUGGING print(var_to_idx)
    
    # Read from args, get corresponding column index of requested variable
    # Maintain order of requested variables
    # Ignores incorrect/misspelled/duplicate variables from simulation
    req_idx = []
    for arg in args:
        if arg in var_to_idx and var_to_idx[arg] not in req_idx:
            req_idx.append(var_to_idx[arg])
    #DEBUGGING print(req_idx)
   
    # Assign these variable names to the output using indices from req_idx
    # Add commas and newline character, then append as first entry into output
    reqvar = ""
    for i in range(len(req_idx)):
        reqvar += varlist[req_idx[i]]
        if i < len(req_idx) - 1:
            reqvar += ','
    reqvar += '\n'
    output.append(reqvar)
    #DEBUGGING print(output)

    # Parses data into pdata such that each entry of pdata is a list representing
    # a row of data from each simulation iteration. Keeps track of number of lines
    # used for simulation iteration data to properly parse data
    pdata = []
    for i in range(num_lines, len(data), num_lines):
        comb_run = []
        for j in range(num_lines):
            comb_run.extend(data[i + j].strip().split())
        pdata.append(comb_run) 
    #DEBUGGING print(pdata)
    
    # Now loop through each entry of pdata, loop through each iteration, and replace
    # 'failed' with 'NaN'
    for i in range(len(pdata)):
        for j, dstring in enumerate(pdata[i]):
            if dstring == 'failed':
                pdata[i][j] = 'NaN'
    #DEBUGGING print(pdata)
   
    # To get the corresponding data from each simulation iteration, loop through each
    # element of pdata, then loop through each "row" and get the corresponding column 
    # Store each simulation iteration data in a temporary  data buffer for appending
    for i in range(len(pdata)):
        data_buf = ""
        for j in range(len(req_idx)):
            data_buf += pdata[i][req_idx[j]]
            if j < len(req_idx) - 1:
                data_buf += ','
            else:
                data_buf += '\n'
                output.append(data_buf)
    #DEBUGGING for value in output:
    #DEBUGGING     print(value)

# Write elements of output line by line to "prelab.txt"
with open(file_out, 'w') as f_o:
    for line in output:
        f_o.write(line)
print(f"Data successfuly parsed to '{file_out}'")

