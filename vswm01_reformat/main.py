from vswm_to_NDA import reformat_vswm_data

# Ensure input file is placed in vswm01_reformat directory 
# or provide full file path
# output file will be placed in vswm01_reformat

# For each participant at a given wave, summary 
# statistics displayed in trial 25 
# Assumes 24 trials per participant
# Returns 24+1 trial rows to include summary statistics
reformat_vswm_data(input("File name:"),'vswm_reformatted.csv')