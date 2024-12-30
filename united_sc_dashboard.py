###################################################################
# Data manipulation packages
import pandas as pd
import numpy as np

# File path
import os

# Data visualization packages
import streamlit as st
from mplsoccer import VerticalPitch  # Ensure this import is included

# External Packages
from data_processing import DataProcessing
from visuals import FootballVisuals
from match_data import MatchData

# Error Handling
import traceback

####################################################################

def plot_shot_maps(total_shots, team, view, competition, season, player):
    """Function to plot shot maps."""
    # Setup the pitch
    pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='#1d2849', line_color='w', half=True, pad_top=20, pad_right=20)
    fig, ax = pitch.draw(figsize=(8, 10))

    # Shot map method
    visuals = FootballVisuals(model_paths={  # Assuming you have model paths defined
        'op': 'Models/expected_goals_model_lr.sav',
        'non_op': 'Models/expected_goals_model_lr_v2.sav'
    })
    visuals.createShotmap(total_shots, pitch=pitch, fig=fig, ax=ax, team=team, view=view, competition=competition, season_year=season, players=player,
                          pitchcolor='#1d2849', shot_color='gray', titlecolor='w', team_color='w', fontfamily='Segoe UI')

    st.write("Viewing shots from matches vs selected opponent(s):")
    st.pyplot(fig)

def display_filtered_shots(total_shots, view, player):
    """Function to display the filtered shots table."""
    if view == "Shots For":
        if player == "All Players":
            filtered_shots = total_shots.copy()  # No filtering, show all players
        else:
            filtered_shots = total_shots[total_shots['Player'] == player]
        filtered_shots = filtered_shots[['Player', 'Team', 'xG', 'outcome', 'shotType', 'situation']]
        filtered_shots.reset_index(drop=True, inplace=True)
    else:
        filtered_shots = total_shots.copy()
        filtered_shots = filtered_shots[['Team', 'xG', 'outcome', 'shotType', 'situation']]
        filtered_shots.reset_index(drop=True, inplace=True)

    # Apply formatting to ensure two decimal places are shown, even for zero
    filtered_shots = filtered_shots.style.format({
        "xG": "{:.2f}"
    })

    st.write(filtered_shots)

def run_dashboard():
    # Define instances
    match_data = MatchData()  # Create instance once at the start

    # Define model paths for DataProcessing
    model_paths = {
        'op': 'Models/expected_goals_model_lr.sav',
        'non_op': 'Models/expected_goals_model_lr_v2.sav'
    }

    # Define instances for processing and visuals
    data_processor = DataProcessing(model_paths)

    # Create Title
    st.title("UPSL Stats Dashboard")

    ####################################################################

    try:
        # Tab Header
        st.header("Shot Maps")

        # Selector for competition - Refine logic when adding US Open Cup
        competition = st.sidebar.selectbox(
            "Competition:", ("UPSL")
        )

        # Selector for competition
        division = st.sidebar.selectbox(
            "Division:", ("Premier")
        )

        conference_names = match_data.get_conference_names()

        # Selector for conference
        default_conference = "Midwest Central"
        # Ensure default conference is in the list
        if default_conference in conference_names:
            default_index = conference_names.index(default_conference)
        else:
            default_index = 0  # Fallback to the first conference if not found

        conference = st.sidebar.selectbox(
            "Conference:",
            options=conference_names,
            index=default_index  # set default index
        )

        # Selector for season
        season = st.sidebar.selectbox(
            "Season:", ("2024 Fall", "2025 Spring")
        )

        team_names = match_data.get_team_names(conference_name=conference)

        # Set the default team based on the selected conference
        default_team = "United SC" if conference == default_conference else team_names[0] if team_names else None

        # Selector for team
        team = st.sidebar.selectbox(
            "Select Team:",
            options=team_names,
            index=team_names.index(default_team) if default_team in team_names else 0  # Set default index
        )

        # Selector for Shots For or Shots Against
        view = st.sidebar.selectbox(
            "Choose Shot Type:",
            ("Shots For", "Shots Against")  # Options
        )

        # Create a DataFrame of the match
        match_df = match_data.get_match_data(conference_name=conference, team_name=team, season=season)

        # Extract opponent names into a list
        opponents = [match["Opponent"] for match in match_df]

        # Multi-select dropdown for matches
        selected_matches = st.multiselect(
            "Select Opponent(s):",
            options=opponents,
            default=opponents  # Default to nothing selected
        )

        team_roster = match_data.get_team_roster(team_name=team, conference_name=conference)

        # Create a selector to choose player to analyze
        if view == "Shots For":
            player = st.selectbox(
                "Select Player:",
                (["All Players"] + team_roster)
            )
        else:
            player = "All Players"  # Default to "All Players" for other view instances

        # Check if any matches are selected
        if selected_matches:
            # Filter the DataFrame based on selected matches
            match_df = pd.DataFrame(match_df)
            filtered_matches = match_df[match_df["Opponent"].isin(selected_matches)]

            try:
                # Read and combine data for selected matches
                dfs_list = []
                data_found = False  # Flag to check if data is found
                for _, row in filtered_matches.iterrows():
                    opponent = row["Opponent"]
                    match_id = row["MatchId"]
                    file_path = f'Competitions/{competition}/{division}/{conference}/{season}/{team}/{match_id}_{opponent}/Raw Data/{team if view == "Shots For" else opponent} Shots.csv'

                    if os.path.exists(file_path):
                        # Attempt to read the file
                        df = pd.read_csv(file_path)
                        df = df.rename(columns={'Team': "H_A"})
                        df['Team'] = team if view == "Shots For" else opponent
                        df['MatchId'] = match_id
                        dfs_list.append(df)
                        data_found = True  # Set flag to True if data is found
                    else:
                        st.warning(f'Missing data for: {opponent} match on {match_id[0:2]}/{match_id[2:4]}/{match_id[4:]}.')  # Notify that the file is missing

                # Combine into a single DataFrame
                if data_found:
                    shot_events = pd.concat(dfs_list, ignore_index=True)
                else:
                    st.write("No Data Available")  # No data found for selected matches

            except FileNotFoundError as e:
                st.error(f"No Data Available")  # Handle file not found error
            except NameError as e:
                st.error(f"A variable or name is not defined. Please verify your code or input: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

        else:
            # Handle the case where no matches are selected
            st.write("No matches selected. Please select one or more matches to view data.")

        ####################################################################

        # Calculate xG from imported file
        total_shots = data_processor.calc_xg(shot_events)

        # Plot the shot maps
        plot_shot_maps(total_shots, team, view, competition, season, player)

        # Display the filtered shots table
        display_filtered_shots(total_shots, view, player)

    # Capture traceback and display it
    except Exception as e:
        st.write(f"No Data Available")

if __name__ == "__main__":
    run_dashboard()