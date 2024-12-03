import pandas as pd

# Define match details for different competitions and seasons
matches_upsl_fall_2024 = [
    {"MatchId": "081724", "Opponent": "Chicago Strikers", "H_A": "Away"},
    {"MatchId": "082424", "Opponent": "Panathinaikos", "H_A": "Home"},
    {"MatchId": "090824", "Opponent": "Wisloka", "H_A": "Home"},
    {"MatchId": "091424", "Opponent": "Round Lake Evolution", "H_A": "Away"},
    {"MatchId": "092124", "Opponent": "Allegiant FC", "H_A": "Home"},
    {"MatchId": "092824", "Opponent": "Berber City", "H_A": "Away"},
    {"MatchId": "100624", "Opponent": "Chicago Nation", "H_A": "Home"},
    {"MatchId": "101924", "Opponent": "Black Cat", "H_A": "Away"},
    {"MatchId": "102724", "Opponent": "Urbana City FC", "H_A": "Away"},
    {"MatchId": "110324", "Opponent": "Diverse City", "H_A": "Home"},
]

matches_upsl_spring_2025 = [
    # Define matches for the Spring 2025 season here
]

matches_us_open_fall_2024 = [
    # Define matches for the Fall 2024 US Open Cup season here
]

# Additional match data can be added for more seasons/competitions as needed

# Function to return match data based on competition and season
def load_matches(competition, season):
    if competition == "UPSL":
        if season == "Fall 2024":
            return pd.DataFrame(matches_upsl_fall_2024)
        elif season == "Spring 2025":
            return pd.DataFrame(matches_upsl_spring_2025)
    elif competition == "US Open Cup":
        if season == "2024":
            return pd.DataFrame(matches_us_open_fall_2024)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no matches found

# Function to retrieve match details by match ID
def get_match_by_id(match_id, competition, season):
    matches = load_matches(competition, season)
    return matches[matches["MatchId"] == match_id]