###################################################################
# File reading packages
import os

# Data visualization packages
import streamlit as st

# Data maninpulation packages
import pandas as pd
import numpy as np

# External Packages
from data_processing import DataProcessing
from match_data import MatchData

###################################################################

# Define instances
match_data = MatchData() # Create instance once at the start

# Define model paths for DataProcessing
model_paths = {
    'op': 'Models/expected_goals_model_lr.sav',
    'non_op': 'Models/expected_goals_model_lr_v2.sav'
}

# Define instances for processing
data_processor = DataProcessing(model_paths)

# Create Title
st.title(f"UPSL Stats Dashboard")

# Define global file paths
current_dir = os.path.dirname(__file__) # Get the current directory of the script

###################################################################

# Error Handling
try:
    # create header
    st.header("Shot Leaders")

    # Selector for competition
    competition = st.sidebar.selectbox(
        "Competition:", ("UPSL", "US Open Cup")
        )

    # Selector for division
    division = st.sidebar.selectbox(
        "Division:", ("Premier") # Add more divisions if avaialble
    )

    # Selector for conference
    conference_names = match_data.get_conference_names()
    default_conference = "Midwest Central"
    default_index = conference_names.index(default_conference) if default_conference in conference_names else 0
    conference = st.sidebar.selectbox(
        "Conference",
        options=conference_names,
        index=default_index # set default index
    )

    # Selector for season
    season = st.sidebar.selectbox(
        "Season:", ("2024 Fall", "2025 Spring")
        )

    # Selector for team
    team_names = match_data.get_team_names(conference_name=conference)
    default_team = "United SC" if conference == default_conference else team_names[0] if team_names else None
    team = st.selectbox(
        "Select Team:",
        options=team_names,
        index=team_names.index(default_team) if default_team in team_names else 0 # Set default index
    )

    # Create a DataFrame of the match
    match_df = match_data.get_match_data(conference_name=conference, team_name=team, season=season)
    match_df = pd.DataFrame(match_df)

        # Read and combine data for selected matches
    dfs_list = []
    for _, row in match_df.iterrows():
        opponent = row["Opponent"]
        match_id = row["MatchId"]
        # Construct the relative path to the CSV file
        file_path = os.path.join(current_dir, '..', 'Competitions', competition, division, conference, season, team, f"{match_id}_{opponent}", 'Raw Data', f'{team} Shots.csv')

        # Check if the file exists before reading
        if os.path.exists(file_path):
            # Attempt to read the file
            df = pd.read_csv(file_path)
            df = df.rename(columns={'Team': "H_A"})
            df['Team'] = team
            df['MatchId'] = match_id
            dfs_list.append(df)
        # else:
            # st.warning(f'File not found: {file_path}. Skipping this match') # Notify that the file is missing

    # Combine into a single DataFrame
    shot_events = pd.concat(dfs_list, ignore_index=True)

    # calc xG from imported file
    total_shots = data_processor.calc_xg(shot_events)

    # Compute metrics
    total_shots["non_penalty_xG"] = total_shots.apply(
        lambda row: row["xG"] if not row["isPenalty"] else 0, axis=1
    )

    summary_df = (
        total_shots.groupby("Player")
        .agg(
            total_shots=("Player", "count"),
            non_penalty_shots=("isPenalty", lambda x: len(x) - x.sum()),
            openplay_shots=("isRegularPlay", "sum"),
            goals=("isGoal", "sum"),
            goals_per_shot=("isGoal", lambda x: x.sum() / len(x) if len(x) > 0 else 0),
            xG=("xG", "sum"),
            xG_per_shot=("xG", lambda x: x.sum() / len(x) if len(x) > 0 else 0),
            non_penalty_xG=("non_penalty_xG", "sum"),
            non_penalty_xG_per_shot=(
                "non_penalty_xG",
                lambda x: x.sum() / (len(x) - total_shots["isPenalty"].sum())
                if (len(x) - total_shots["isPenalty"].sum()) > 0
                else 0,
            ),
        )
        .reset_index()
    )

    # Adding 'Goals - xG' column
    summary_df["goals_minus_xG"] = summary_df["goals"] - summary_df["xG"]

    # reset index and drop index column
    summary_df = summary_df.reset_index(drop=True)

    # Rename columns
    summary_df = summary_df.rename(
        columns={
            "total_shots": "Shots",
            "non_penalty_shots": "Non-Penalty Shots",
            "openplay_shots": "Open Play Shots",
            "goals": "Goals",
            "goals_per_shot": "Shooting Accuracy (Goals per Shot)",
            "xG": "Expected Goals (xG)",
            "xG_per_shot": "Shooting Efficiency (xG per Shot)",
            "non_penalty_xG": "Non-Penalty xG",
            "non_penalty_xG_per_shot": "Non-Penalty xG per Shot",
            "goals_minus_xG": "Finishing (Goals minus xG)",
        }
    )

    # Create a df with player data and concatenate with summary_df
    player_data = match_data.get_player_data(conference_name=conference, team_name=team)

    # Change NA values in Appearances to 0
    player_data['Appearances'] = player_data['Appearances'].replace("N/A", 0)

    # Change Appearances to int data type
    player_data['Appearances'] = player_data['Appearances'].astype(int)

    # Format Position to have only the first letter capitalized and the rest lower case
    player_data['Position'] = player_data['Position'].str.capitalize()

    # Merge player data with summary_df based on Player
    summary_df = pd.merge(player_data, summary_df, on="Player", how="left")
    # Convert specific columns to int
    summary_df['Shots'] = summary_df['Shots'].fillna(0).astype(int)
    summary_df['Non-Penalty Shots'] = summary_df['Non-Penalty Shots'].fillna(0).astype(int)
    summary_df['Open Play Shots'] = summary_df['Open Play Shots'].fillna(0).astype(int)
    summary_df['Goals'] = summary_df['Goals'].fillna(0).astype(int)
    # Replace all None values in summary_df with 0
    summary_df = summary_df.fillna(0)

    # Apply formatting to ensure two decimal places are shown, even for zero
    summary_df = summary_df.style.format({
        "Shooting Accuracy (Goals per Shot)": "{:.2f}",
        "Expected Goals (xG)": "{:.2f}",
        "Shooting Efficiency (xG per Shot)": "{:.2f}",
        "Non-Penalty xG": "{:.2f}",
        "Non-Penalty xG per Shot": "{:.2f}",
        "Finishing (Goals minus xG)": "{:.2f}"
    })

    st.dataframe(summary_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.write(f"{e}")