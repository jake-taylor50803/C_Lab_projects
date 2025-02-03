import pandas as pd

def reformat_vswm_data(input_csv, output_csv):

    # Read input file into dataframe
    df = pd.read_csv(input_csv)

    # Map the `vswm_stimulus_set` column
    stimulus_mapping = {'Group A': 1, 'Group B': 2, 'Group C': 3, 'Group D': 4}
    df['vswm_stimulus_set'] = df['vswm_stimulus_set'].replace(stimulus_mapping)

    # Extract trial-specific data
    trial_data = []
    for trial_num in range(1, 25):  # Assuming 24 trials
        set_size_col = f"vswm_trial{trial_num}_set_size"
        accuracy_col = f"vswm_trial{trial_num}_accuracy"

        if set_size_col in df.columns and accuracy_col in df.columns:
            # Add input data to trial_subset
            trial_subset = df[[
                "subject_id", "interview_date", "interview_age", "sex", "group", 
                "wave", "filename", "comments_misc", "vswm_stimulus_set", 
                set_size_col, accuracy_col,  # Trial-specific columns
                "vswm_set3_score", "vswm_set4_score", "vswm_set5_score", "vswm_set6_score",  # Accuracy columns
                "vswm_total_score"  # Total score
            ]].copy()
            # Add trial number as a separate column
            trial_subset["trial"] = trial_num
            # Rename columns for NDA format
            trial_subset.rename(columns={
                set_size_col: "vswm_trial_set_size",
                accuracy_col: "vswm_trial_accuracy"
            }, inplace=True)
            # Extract numeric part of datapoint only for NDA format
            trial_subset["vswm_trial_set_size"] = trial_subset["vswm_trial_set_size"].str.extract(r'(\d+)').astype(int)

            # Append processed data for each trial per participant to main data list
            trial_data.append(trial_subset)

    # Combine all trial data into one dataframe
    trial_df = pd.concat(trial_data)

    # Rename and calculate required fields for the output format
    trial_df.rename(columns={
        "subject_id": "src_subject_id",
        "sex" : "gender",
        "wave": "timepoint_wave",
        "vswm_stimulus_set": "vswm_stimulus_set"
    }, inplace=True)

    # Add placeholders or calculated fields for the remaining columns
    trial_df["session"] = None
    trial_df["visit"] = None
    trial_df["task"] = "vswm"
    trial_df["stimcorss3"] = None
    trial_df["stimcorss4"] = None
    trial_df["stimcorss5"] = None
    trial_df["stimcorss6"] = None
    trial_df["isidur"] = None
    trial_df["total_rs"] = None
    trial_df["dtttest_percor"] = None
    trial_df["accuracy_ss3"] = None
    trial_df["accuracy_ss4"] = None
    trial_df["accuracy_ss5"] = None
    trial_df["accuracy_ss6"] = None
    trial_df["rt_ss3"] = None
    trial_df["rt_ss4"] = None
    trial_df["rt_ss5"] = None
    trial_df["rt_ss6"] = None

    # Compute summary rows for total_rs, dtttest_percor, and accuracy_ss3-6
    summary_rows = []
    # Group trial data by participant and wave to get proper summary stats for each timepoint
    for (subject, wave), group in trial_df.groupby(["src_subject_id", "timepoint_wave"]):
        # extract accuracy, total raw score, and compute percentage from total raw
        total_rs = group["vswm_total_score"].iloc[0]
        dtttest_percor = (total_rs / 24) * 100 # assuming 24 trials
        accuracy_ss3 = group["vswm_set3_score"].iloc[0]
        accuracy_ss4 = group["vswm_set4_score"].iloc[0]
        accuracy_ss5 = group["vswm_set5_score"].iloc[0]
        accuracy_ss6 = group["vswm_set6_score"].iloc[0]
        stimulus_set = group["vswm_stimulus_set"].iloc[0]
        interview_date = group["interview_date"].iloc[0]
        interview_age = group["interview_age"].iloc[0]
        gender = group["gender"].iloc[0]

        # Create summary row containing interview/participant info and summary stats
        summary_row = {
            "src_subject_id": subject,
            "timepoint_wave": wave,
            "total_rs": total_rs,
            "dtttest_percor": dtttest_percor,
            "accuracy_ss3": accuracy_ss3,
            "accuracy_ss4": accuracy_ss4,
            "accuracy_ss5": accuracy_ss5,
            "accuracy_ss6": accuracy_ss6,
            "session": None,
            "visit": None,
            "task": "vswm",
            "vswm_stimulus_set" : stimulus_set,
            "interview_date" : interview_date,
            "interview_age" : interview_age,
            "gender" : gender
        }

        # add each new row to summary rows group
        summary_rows.append(summary_row)

    # Convert summary rows to DataFrame and append to trial_df
    summary_df = pd.DataFrame(summary_rows)
    trial_df = pd.concat([trial_df, summary_df], ignore_index=True)

    # Reorder columns to match the desired output format
    output_columns = [
        "subjectkey", "src_subject_id", "interview_date", "interview_age", "gender", 
        "session", "visit", "task", "stimcorss3", "stimcorss4", "stimcorss5", 
        "stimcorss6", "isidur", "total_rs", "dtttest_percor", "accuracy_ss3", 
        "accuracy_ss4", "accuracy_ss5", "accuracy_ss6", "rt_ss3", "rt_ss4", 
        "rt_ss5", "rt_ss6", "timepoint_wave", "comments_misc", "trial", 
        "vswm_stimulus_set", "vswm_trial_set_size", "vswm_trial_accuracy"
    ]
    trial_df = trial_df.reindex(columns=output_columns)

    # Sort by trial per wave per subject with summary stats at the end of each participant * wave group
    trial_df["trial"] = trial_df["trial"].fillna(9999)
    trial_df = trial_df.sort_values(by=["src_subject_id", "timepoint_wave","trial", ])
    trial_df["trial"] = trial_df["trial"].replace(9999, "")

    # Write the reformatted data to the output CSV
    trial_df.to_csv(output_csv, index=False)

