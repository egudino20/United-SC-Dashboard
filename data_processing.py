import pandas as pd
import numpy as np
import pickle
import sklearn

class DataProcessing:
    def __init__(self, model_paths):
        """Initialize the DataProcessing class with model paths."""
        self.loaded_models = self._load_models(model_paths)

    def _load_models(self, model_paths):
        """Load machine learning models from disk."""
        models = {}
        for key, path in model_paths.items():
            models[key] = pickle.load(open(path, 'rb'))
        return models

    def data_preparation(self, df):
        """Prepare the data by creating multifeature attributes."""
        df['isLeftFooted'] = np.where((df['shotRightFoot'] == False) & (df['shotLeftFoot'] == True), 1, 0)
        df['isRightFooted'] = np.where((df['shotRightFoot'] == True) & (df['shotLeftFoot'] == False), 1, 0)
        df['isHead'] = np.where(df['shotBodyType'] == 'Head', 1, 0)
        df['isOtherBodyType'] = np.where(df['shotBodyType'] == 'OtherBodyPart', 1, 0)
        df['isRegularPlay'] = np.where(df['situation'] == 'OpenPlay', 1, 0)
        df['isThrowIn'] = np.where(df['throwIn'] == True, 1, 0)
        df['isDirectFree'] = np.where(df['situation'] == 'DirectFreekick', 1, 0)
        df['isFromCorner'] = np.where(df['situation'] == 'FromCorner', 1, 0)
        df['isSetPiece'] = np.where(df['situation'] == 'SetPiece', 1, 0)
        df['isOwnGoal'] = np.where(df['goalOwn'] == True, 1, 0)
        df['isPenalty'] = np.where(df['situation'] == 'Penalty', 1, 0)
        df['isGoal'] = np.where(df['isGoal'] == True, 1, 0)

    def calc_xg(self, events_df):
        """Calculate expected goals (xG) based on event data."""
        # Splitting the 'Event' column into new columns
        events_df[['type', 'shotType', 'situation', 'outcome']] = events_df['Event'].str.split(' ', expand=True)

        # Rename the 'Event' column to 'type'
        events_df.rename(columns={'X': 'x', 'Y': 'y'}, inplace=True)

        # Creating new columns based on the split 'type' data
        events_df['shotRightFoot'] = events_df['shotType'].apply(lambda x: True if x == 'Right' else False)
        events_df['shotLeftFoot'] = events_df['shotType'].apply(lambda x: True if x == 'Left' else False)
        events_df['shotBodyType'] = events_df['shotType'].apply(lambda x: 'Head' if x == 'Head' else ('Foot' if x in ['Right', 'Left'] else 'OtherBodyPart'))
        events_df['throwIn'] = events_df['situation'].apply(lambda x: True if x == 'ThrowIn' else False)
        events_df['goalOwn'] = events_df['Event'].apply(lambda x: True if 'Own Goal' in x else False)
        events_df['isGoal'] = events_df['outcome'].apply(lambda x: True if x == 'Goal' else False)

        total_shots = events_df.loc[events_df['type'] == 'Shot'].reset_index(drop=True)

        # Prepare data
        self.data_preparation(total_shots)

        total_shots['distance_to_goal'] = np.sqrt(((100 - total_shots['x'])**2) + ((total_shots['y'] - (100/2))**2))
        total_shots['distance_to_center'] = abs(total_shots['y'] - 100/2)
        total_shots['angle'] = np.absolute(np.degrees(np.arctan((abs((100/2) - total_shots['y'])) / (100 - total_shots['x']))))
        total_shots['isFoot'] = np.where(((total_shots['isLeftFooted'] == 1) | (total_shots['isRightFooted'] == 1)) & (total_shots['isHead'] == 0), 1, 0)

        features_op = ['distance_to_goal', 'angle', 'isFoot', 'isHead']
        features_non_op = ['distance_to_goal', 'angle', 'isFoot', 'isHead', 'isDirectFree', 'isSetPiece', 'isFromCorner']

        # Open play shots
        total_shots_op = total_shots.loc[total_shots['isRegularPlay'] == 1]
        shots_df_op = total_shots_op[features_op]
        total_shots.loc[total_shots['isRegularPlay'] == 1, 'xG'] = self.loaded_models['op'].predict_proba(shots_df_op)[:, 1]

        # Set-piece shots (excluding penalties)
        total_shots_non_op = total_shots.loc[(total_shots['isRegularPlay'] == 0) & (total_shots['isPenalty'] == 0)]
        shots_df_non_op = total_shots_non_op[features_non_op]
        total_shots.loc[(total_shots['isRegularPlay'] == 0) & (total_shots['isPenalty'] == 0), 'xG'] = self.loaded_models['non_op'].predict_proba(shots_df_non_op)[:, 1]

        # Penalty shots
        total_shots.loc[total_shots['isPenalty'] == 1, 'xG'] = 0.79

        return total_shots