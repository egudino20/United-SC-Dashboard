import pandas as pd
import json
from pathlib import Path

class MatchData:
    def __init__(self):
        """Initialize the MatchData class with UPSL data and match definitions."""
        self.upsl_data = self._load_upsl_data()

    def _load_upsl_data(self):
        """Load the UPSL data from the JSON file (private method)."""
        json_path = Path(__file__).parent / 'upsl_data.json'
        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: UPSL data file not found at {json_path}")
            return {}

    def get_conference_names(self):
        """Extract all conference names from the UPSL data structure."""
        conferences = []
        for division in self.upsl_data.get("Division", {}).values():
            if "Conference" in division:
                conferences.extend(division["Conference"].keys())
        return conferences

    def get_team_names(self, conference_name):
        """Extract all team names from the UPSL data structure for a selected conference."""
        teams = []
        for division in self.upsl_data.get("Division", {}).values():
            if "Conference" in division and conference_name in division['Conference']:
                teams.extend(division['Conference'][conference_name].get("Teams", []))
            return teams

    def get_team_roster(self, conference_name, team_name):
        """Retrieve player names"""
        player_names = []
        # Access the specified conference
        conference = self.upsl_data.get("Division", {}).get("Premier", {}).get("Conference", {}).get(conference_name, {})
        # Access the specified team
        team = conference.get("Teams", {}).get(team_name, {})
        # Extract player names from the roster
        for player in team.get("Roster", []):
            player_names.append(player["Player"])
        return player_names

    def get_player_data(self, conference_name, team_name):
        """Retrieve the team roster as a DataFrame with Player, Position, and Appearances."""
        # Access the specified conference
        conference = self.upsl_data.get("Division", {}).get("Premier", {}).get("Conference", {}).get(conference_name, {})
        # Access the specified team
        team = conference.get("Teams", {}).get(team_name, {})
        
        # Create a list to hold player data
        roster_data = []
        # Extract player data from the roster
        for player in team.get("Roster", []):
            roster_data.append({
                "Player": player["Player"],
                "Position": player["Position"],
                "Appearances": player["Appearances"]
            })
        
        # Convert the list to a DataFrame
        return pd.DataFrame(roster_data)

    def get_match_data(self, conference_name, team_name, season):
        """Retrieve match details for a specific team in a given conference."""
        match_data = []
        # Access the specified conference
        conference = self.upsl_data.get("Division", {}).get("Premier", {}).get("Conference", {}).get(conference_name, {})
        # Access the specified team
        team = conference.get("Teams", {}).get(team_name, {})
        
        # Check if the team has matches
        if f"Matches {season}" in team:
            for match in team[f"Matches {season}"]:
                match_id = str(match["Date"].replace("/", ""))  # Format the date as MMDDYY
                opponent = match["Away Team"] if match["Home Team"] == team_name else match["Home Team"]
                home_away = "Home" if match["Home Team"] == team_name else "Away"

                # Append the match data to the list
                match_data.append({
                    "MatchId": match_id,
                    "Opponent": opponent,
                    "H_A": home_away
                })

        return match_data

    def get_match_by_id(self, match_id, competition, season):
        """Retrieve match details by match ID."""
        matches = self.load_matches(competition, season)
        return matches[matches["MatchId"] == match_id]

