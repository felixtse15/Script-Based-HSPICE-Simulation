# Script-Based HSPICE Simulation for Driver Optimization

#A project for ELEC 521: Advanced Digital IC Design (Fall 2025) exploring automated circuit optimization using Python and HSPICE.

- This repository contains the scripts and simulation files used to find the optimal number of stages and driver sizes for an inverter chain driving a large capacitive load. [cite_start]The core of this project is a Python script that automates HSPICE simulations to iteratively minimize propagation delay using a gradient descent algorithm

##  Objective

- The goal of this experiment is to optimize the circuit shown below to determine the ideal number of inverter stages and the specific driver size for each stage to achieve minimum delay
- The circuit under test consists of an initial driver (X1) followed by a chain of inverters driving a load of 50fF and 32 additional 1fF capacitors

![Circuit Diagram](documentation/bitline.png)

## Methodology

1.  A copy of the base SPICE netlist is created to avoid modifying the original file
2.  For a given number of stages (N), the script adds N inverter instantiations and N corresponding size parameters to the netlist copy
3.  Initial sizes for the inverter stages are set based on a geometric progression (e.g., `scale^1`, `scale^2`, ...)
4.  A baseline HSPICE simulation is run to measure the initial delay from the `.mt0` file
5.  The script then "wiggles" each stage's size parameter one by one, running a new simulation for each change to measure the resulting delays
6.  By comparing the altered delays to the baseline delay, a gradient is calculated
7.  The gradient is used to update all stage sizes simultaneously to move towards a lower delay (`new_size = old_size - learning_rate * gradient`)
8.  A new baseline simulation is run with the updated sizes to get a new base delay
9.  This process repeats until the sizes converge or a maximum of 20 iterations is reached

---

## Key Results

- Simulations were run for configurations with 1, 3, 5, 7, and 9 stages. The analysis concluded that a **3-stage design** provides the optimal delay

**Optimal Configuration**: 3 inverter stages 
**Minimum Delay Achieved**: **160.41 ps** 
**Optimized Stage Sizes (multipliers)**: `[2.68, 6.39, 15.85]` 
**Energy Consumption**: 0.68 pJ 

### Comparison with Logical Effort

A theoretical delay was calculated using the method of logical effort to validate the simulation results

**HSPICE Simulated Delay**: 160.41 ps 
**Hand-Calculated Delay**: 145.98 ps 
**Difference**: 8.99% 



