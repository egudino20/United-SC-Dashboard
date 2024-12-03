
###################################################################
# Data maninpulation packages
import pandas as pd
import numpy as np

# Data visualization packages
import streamlit as st
#from st_aggrid import AgGrid, GridOptionsBuilder
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.lines import Line2D
from mplsoccer import Pitch, VerticalPitch, FontManager
from highlight_text import fig_text, ax_text, HighlightText
from matplotlib.patches import Circle
import matplotlib.transforms as transforms

# External Packages
from data_processing import data_preparation, calc_xg
from visuals import createShotmap
from match_data import load_matches

####################################################################

# Define team
team = "United SC"

# Create Title
st.title(f"{team} Stats Dashboard")

# Create tabs
tab = st.sidebar.radio("Select a tab:", ("Shot Maps", "Shot Leaders"))

if tab == "Shot Maps":

    # Error Handling
    try:

        # Tab Header
        st.header("Shot Maps")

        # Selector for competition
        competition = st.sidebar.selectbox(
            "Competition:", ("UPSL", "US Open Cup")
        )

        # Selector for season
        season = st.sidebar.selectbox(
            "Season:", ("Fall 2024", "Spring 2025")
        )

        # Create a DataFrame of the match
        match_df = load_matches(competition=competition, season=season)

        # Selector for Shots For or Shots Against
        view = st.sidebar.selectbox(
            "Choose Shot Type:",
            ("Shots For", "Shots Against")  # Options
        )

        # Multi-select dropdown for matches
        selected_matches = st.sidebar.multiselect(
            "Select Opponent(s):",
            options=match_df["Opponent"],
            default=match_df["Opponent"],  # Default to nothing selected
        )

        # Create a selector to choose player to analyze
        if view == "Shots For":
        if view == "Shots For":
            player = st.selectbox(
                "Select Player:",
                ("All Players", "Andres Castellanos", "Andrii Pityliak", "Brennan Wu",
                "Enrique Gudino De Grote", "Gavin Johnson", "Gerardo Espinoza",
                "Ian M. Murray", "Jacob Sullivan Golda", "Jamie R. Beamish",
                "Landon Johnson", "MacKenzie Bechard", "Moritz Seban",
                "Peter Beasley", "Peter Horner", "Rom Brown", "Ryan Olans",
                "Shamik Patel", "Tapiwa F. Machingauta")
            )
        else:
            player = "All Players"  # Default to "All Players" for other view instances

        # Check if any matches are selected
        if selected_matches:
            # Filter the DataFrame based on selected matches
            filtered_matches = match_df[match_df["Opponent"].isin(selected_matches)]

            try:
                # Read and combine data for selected matches
                dfs_list = []
                for _, row in filtered_matches.iterrows():
                    opponent = row["Opponent"]
                    match_id = row["MatchId"]
                    file_path = f'Competitions/{competition}/{season}/Matches/{opponent}/Raw Data/{team if view == "Shots For" else opponent} Shots.csv'

                    # Attempt to read the file
                    df = pd.read_csv(file_path)
                    df = df.rename(columns={'Team': "H_A"})
                    df['Team'] = team if view == "Shots For" else opponent
                    df['MatchId'] = match_id
                    dfs_list.append(df)

                # Combine into a single DataFrame
                shot_events = pd.concat(dfs_list, ignore_index=True)

            except FileNotFoundError as e:
                st.error(f"File not found for a selected match. Please check data files: {e}")
            except NameError as e:
                st.error(f"A variable or name is not defined. Please verify your code or input: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

        else:
            # Handle the case where no matches are selected
            st.write("No matches selected. Please select one or more matches to view data.")

        ####################################################################

        # calc xG from imported file
        total_shots = calc_xg(shot_events)

        # Setup the pitch
        pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='#1d2849', line_color='w', half=True, pad_top=20, pad_right=20)
        fig, ax = pitch.draw(figsize=(8, 10))

        # shot map method
        createShotmap(total_shots, pitch=pitch, fig=fig, ax=ax, team=team, view=view, competition=competition, season_year=season, players=player, 
                    pitchcolor='#1d2849', shot_color='gray', titlecolor='w', team_color='w', fontfamily='Segoe UI')

        st.write("Viewing shots from matches vs selected opponent(s):")

        # Display the plot
        st.pyplot(fig)

        # show data set for only selected player shots
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

    except Exception as e:
        st.write("No Data Available")

####################################################################
elif tab == "Shot Leaders":
    # create header
    st.header("Shot Leaders")

    # Selector for competition
    competition = st.sidebar.selectbox(
        "Competition:", ("UPSL", "US Open Cup")
        )

    # Selector for season
    season = st.sidebar.selectbox(
        "Season:", ("Fall 2024", "Spring 2025")
        )

    # Create a DataFrame of the match
    match_df = load_matches(competition=competition, season=season)

        # Read and combine data for selected matches
    dfs_list = []
    for _, row in match_df.iterrows():
        opponent = row["Opponent"]
        match_id = row["MatchId"]
        file_path = f'Competitions/{competition}/{season}/Matches/{opponent}/Raw Data/{team} Shots.csv'

        # Attempt to read the file
        df = pd.read_csv(file_path)
        df = df.rename(columns={'Team': "H_A"})
        df['Team'] = team
        df['MatchId'] = match_id
        dfs_list.append(df)

    # Combine into a single DataFrame
    shot_events = pd.concat(dfs_list, ignore_index=True)

    # calc xG from imported file
    total_shots = calc_xg(shot_events)

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