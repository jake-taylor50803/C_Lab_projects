import pandas as pd

def reformat_scr_data(input_csv, output_csv):
   
    # Read input file into dataframe
    df = pd.read_csv(input_csv)

    # Extract trial-specific data
    trial_data = []
    for trial_num in range(1,121): # Assuming 120 trials
        trial_type_col = f"sc_trial{trial_num}_type"
        trial_rt_col = f"sc_trial{trial_num}_rt"
        trial_accuracy_col = f"sc_trial{trial_num}_accuracy"

        if all(col in df.columns for col in [trial_type_col, trial_rt_col, trial_accuracy_col]):
            trial_subset = df[[
                "subject_id", "interview_date", "interview_age", "sex", "wave", 
                "comments_misc", "sc_reaction_time_units", 
                "sc_num_shift_trials", "sc_num_noshift_trials", "sc_total_num_trials",
                trial_type_col, trial_rt_col, trial_accuracy_col
            ]].copy()

            # Add trial number as column
            trial_subset["trial"] = trial_num

            # Rename trial-specific columns to match NDA format
            trial_subset.rename(columns={
                trial_type_col: "sc_trial_type",
                trial_rt_col: "sc_trial_rt",
                trial_accuracy_col: "sc_trial_accuracy",
                "subject_id": "src_subject_id",
                "sex": "gender",
                "wave": "timepoint_wave"
            }, inplace=True)

            # Combine all trial data into one DataFrame
            trial_data.append(trial_subset)
    
    # Combine all trial data into one Dataframe
    trial_df = pd.concat(trial_data)

    # Convert Shift and NoShift strings to 1 or 2 respectively
    trial_df["sc_trial_type"] = trial_df["sc_trial_type"].replace({"Shift": 1, "NoShift": 2})

    # Add placeholders or calculated fields for the remaining summary columns
    trial_df["sc_shift_corr_mean_rt"] = None
    trial_df["sc_shift_corr_sd_rt"] = None
    trial_df["num_corr_shift_trials"] = None
    trial_df["sc_shift_incorr_mean_rt"] = None
    trial_df["sc_shift_incorr_sd_rt"] = None
    trial_df["num_incorr_shift_trials"] = None
    trial_df["sc_noshift_corr_mean_rt"] = None
    trial_df["sc_noshift_corr_sd_rt"] = None
    trial_df["num_corr_noshift_trials"] = None
    trial_df["sc_noshift_incorr_mean_rt"] = None
    trial_df["sc_noshift_incorr_sd_rt"] = None
    trial_df["num_incorr_noshift_trials"] = None
    trial_df["sc_shift_accuracy"] = None
    trial_df["sc_noshift_accuracy"] = None

    # Compute combined summary statistics for shift and no-shift trials
    summary_rows = []
    for (subject, wave), group in trial_df.groupby(["src_subject_id", "timepoint_wave"]):
        # General
        date = group["interview_date"].iloc[0]
        age = group["interview_age"].iloc[0]
        gender = group["gender"].iloc[0]
        

        # Retrieve summary statistics directly from the input DataFrame
        shift_stats = df[df["subject_id"] == subject]
        if not shift_stats.empty:
            shift_corr_mean_rt = shift_stats["sc_shift_corr_mean_rt"].values[0]
            shift_corr_sd_rt = shift_stats["sc_shift_corr_sd_rt"].values[0]
            num_corr_shift_trials = shift_stats["num_corr_shift_trials"].values[0]
            shift_incorr_mean_rt = shift_stats["sc_shift_incorr_mean_rt"].values[0]
            shift_incorr_sd_rt = shift_stats["sc_shift_incorr_sd_rt"].values[0]
            num_incorr_shift_trials = shift_stats["num_incorr_shift_trials"].values[0]
            shift_accuracy = shift_stats["sc_shift_accuracy"].values[0]

            noshift_corr_mean_rt = shift_stats["sc_noshift_corr_mean_rt"].values[0]
            noshift_corr_sd_rt = shift_stats["sc_noshift_corr_sd_rt"].values[0]
            num_corr_noshift_trials = shift_stats["num_corr_noshift_trials"].values[0]
            noshift_incorr_mean_rt = shift_stats["sc_noshift_incorr_mean_rt"].values[0]
            noshift_incorr_sd_rt = shift_stats["sc_noshift_incorr_sd_rt"].values[0]
            num_incorr_noshift_trials = shift_stats["num_incorr_noshift_trials"].values[0]
            noshift_accuracy = shift_stats["sc_noshift_accuracy"].values[0]
        else:
            shift_corr_mean_rt = None
            shift_corr_sd_rt = None
            num_corr_shift_trials = None
            shift_incorr_mean_rt = None
            shift_incorr_sd_rt = None
            num_incorr_shift_trials = None
            shift_accuracy = None
            noshift_corr_mean_rt = None
            noshift_corr_sd_rt = None
            num_corr_noshift_trials = None
            noshift_incorr_mean_rt = None
            noshift_incorr_sd_rt = None
            num_incorr_noshift_trials = None
            noshift_accuracy = None



        # Create a single summary row for the participant and wave
        summary_row = {
            "src_subject_id": subject,
            "interview_date": date,
            "interview_age": age,
            "gender": gender,
            "timepoint_wave": wave,
            "sc_shift_corr_mean_rt": shift_corr_mean_rt,
            "sc_shift_corr_sd_rt": shift_corr_sd_rt,
            "num_corr_shift_trials": num_corr_shift_trials,
            "sc_shift_incorr_mean_rt": shift_incorr_mean_rt,
            "sc_shift_incorr_sd_rt": shift_incorr_sd_rt,
            "num_incorr_shift_trials": num_incorr_shift_trials,
            "sc_shift_accuracy": shift_accuracy,
            "sc_noshift_corr_mean_rt": noshift_corr_mean_rt,
            "sc_noshift_corr_sd_rt": noshift_corr_sd_rt,
            "num_corr_noshift_trials": num_corr_noshift_trials,
            "sc_noshift_incorr_mean_rt": noshift_incorr_mean_rt,
            "sc_noshift_incorr_sd_rt": noshift_incorr_sd_rt,
            "num_incorr_noshift_trials": num_incorr_noshift_trials,
            "sc_noshift_accuracy": noshift_accuracy,
            
        }

        # Append the summary row
        summary_rows.append(summary_row)

    # Convert summary rows to DataFrame
    summary_df = pd.DataFrame(summary_rows)

    # Append the summary rows to the trial DataFrame
    trial_df = pd.concat([trial_df, summary_df], ignore_index=True)


    # Reorder columns to match the desired output format
    output_columns = [
        "subjectkey", "src_subject_id", "interview_date", "interview_age", "gender", 
        "timepoint_wave", "comments_misc", "trial", "sc_reaction_time_units", 
        "sc_num_shift_trials", "sc_num_noshift_trials", "sc_total_num_trials",
        "sc_trial_type", "sc_trial_rt", "sc_trial_accuracy",
        "sc_shift_corr_mean_rt", "sc_shift_incorr_mean_rt", "sc_noshift_corr_mean_rt", 
        "sc_noshift_incorr_mean_rt", "sc_shift_corr_sd_rt", "sc_shift_incorr_sd_rt", 
        "sc_noshift_corr_sd_rt", "sc_noshift_incorr_sd_rt", "sc_shift_accuracy", 
        "sc_noshift_accuracy"
    ]

        

    # Reindex into output columns
    trial_df = trial_df.reindex(columns=output_columns)

    # Sort by trial per wave per subject
    trial_df["trial"] = trial_df["trial"].fillna(9999)  # Assign a large number to summary rows for sorting
    trial_df = trial_df.sort_values(by=["src_subject_id", "timepoint_wave", "trial"])
    trial_df["trial"] = trial_df["trial"].replace(9999, "")  # Remove trial number for summary rows


    # Write reformatted data to output CSV
    trial_df.to_csv(output_csv, index=False)

