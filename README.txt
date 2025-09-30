ELEC521 Lab 1.2, Felix Tse, 9/26/2025

-This zip file contains ft33_optimize.py (the optimization script), ft33_netlist.sp (spice netlist), and ft33_parse.py (a modified version of ft33_prelab.py which was turned in for Lab 1.1).

-MUST USE ft33_parse.py, NOT ft33_prelab.py. This script has been modified to take input filenames and output filenames as arguments from the command line, which greatly simplifies the task 
 of parsing different files in the optimization script. All other functionality is unchanged between the two.

-In ft33_optimize.py, to run for different stages, change the global constant "NUM_STAGES" to run simulations for different stages. ft33_optimize.py also assumes that the hspice 
 simulator is in the path "/clear/apps/elec8/bin/hspice" 

-For 7 or more stages, also change the global constant "INITIAL_SCALE" to 1.5, or else Skyworks PDK will give a sizing error.

-Many intermediate files will be generated from ft33_optimize.py, including all the .mt* files from HSPICE .alter simulations, and output*.txt, the result of parsing for delay and 
 total energy. These files can be ignored: all results are printed directly to console output.