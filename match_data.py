import pandas as pd
import json
from pathlib import Path

class MatchData:
    def __init__(self):
        """Initialize the MatchData class with UPSL data and match definitions."""
        self.upsl_data = self._load_upsl_data()
        
        # Define match details for different competitions and seasons
        self.matches_upsl_fall_2024 = [
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
        
        self.matches_upsl_spring_2025 = []
        self.matches_us_open_fall_2024 = []

    def _load_upsl_data(self):
        """Load the UPSL data from the JSON file (private method)."""
        json_path = Path(__file__).parent / 'upsl_data.json'
        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: UPSL data file not found at {json_path}")
            return {}

    def load_matches(self, competition, season):
        """Return match data based on competition and season."""
        if competition == "UPSL":
            if season == "Fall 2024":
                return pd.DataFrame(self.matches_upsl_fall_2024)
            elif season == "Spring 2025":
                return pd.DataFrame(self.matches_upsl_spring_2025)
        elif competition == "US Open Cup":
            if season == "2024":
                return pd.DataFrame(self.matches_us_open_fall_2024)
        return pd.DataFrame()

    def get_match_by_id(self, match_id, competition, season):
        """Retrieve match details by match ID."""
        matches = self.load_matches(competition, season)
        return matches[matches["MatchId"] == match_id]

    def get_conference_names(self):
        """Extract all conference names from the UPSL data structure."""
        conferences = []
        for division in self.upsl_data.get("Division", {}).values():
            if "Conference" in division:
                conferences.extend(division["Conference"].keys())
        return conferences