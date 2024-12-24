# data manipulation and analysis
import pandas as pd
import numpy as np
from data_processing import DataProcessing

# data visualization
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.lines import Line2D
from mplsoccer import Pitch, VerticalPitch, FontManager
from highlight_text import fig_text, ax_text, HighlightText
from matplotlib.patches import Circle
import matplotlib.transforms as transforms

# machine learning
import pickle
import sklearn

class FootballVisuals:
    def __init__(self, model_paths):
        """Initialize the FootballVisuals class with default parameters."""
        self.data_processing = DataProcessing(model_paths) # Create an instance of DataProcessing

    def createShotmap(self, events_df, fig, ax, pitch, team, players, view, competition, season_year, pitchcolor, shot_color, titlecolor, team_color, fontfamily):
        """Create a shot map visualization"""
        # Prepate the data using DataProcessing instance
        total_shots = self.data_processing.calc_xg(events_df)

        # Convert coordinates to statsbomb
        total_shots.x = total_shots.x * 1.2
        total_shots.y = (100 - total_shots.y) * 0.8

        #Filter by Player
        if players != "All Players":
            total_shots = total_shots[total_shots['Player'] == players]
        else:
            pass
        
        # Create goal mask
        mask_goal = total_shots['isGoal'] == True

        pitch.scatter(total_shots.loc[mask_goal, 'x'], 80-total_shots.loc[mask_goal, 'y'], s=(total_shots.loc[mask_goal, 'xG'] * 1900) + 100,
                    zorder=3, edgecolor='w', linewidths=2.5, c='red', label='Goal', alpha=0.6, ax=ax)
        pitch.scatter(total_shots.loc[~mask_goal, 'x'], 80-total_shots.loc[~mask_goal, 'y'],
                    edgecolor='w', linewidths=2.5, c=shot_color, s=(total_shots.loc[~mask_goal, 'xG'] * 1900) + 100, zorder=2,
                    label='No Goal', ax=ax)
        
        # Add title and stats summary
        if players != 'All Players':
            ax.text(40, 135, f'{players} | {team}', fontsize=22, color='w', ha='center', fontweight='bold', fontfamily=fontfamily)
        else:
            ax.text(40, 135, f'{team}', fontsize=22, color='w', ha='center', fontweight='bold', fontfamily=fontfamily)
        
        ax.text(40, 131.25, f'{view} - {competition} {season_year}', fontsize=16, color='w', ha='center', fontweight='bold', fontfamily=fontfamily)
        
        goals = len(total_shots[total_shots["isGoal"] == True])
        xg_sum = total_shots['xG'].sum()
        num_chances = len(total_shots)
        xg_per_chance = xg_sum / num_chances
        penalties_scored = len(total_shots[(total_shots['isPenalty'] == 1) & (total_shots['isGoal'] == True)])
        penalties_taken = len(total_shots[total_shots['isPenalty'] == 1])

        op_shots = total_shots[total_shots['isRegularPlay'] == 1]
        non_op_shots = total_shots[total_shots['isRegularPlay'] == 0]
        pk_shots = total_shots[total_shots['isPenalty'] == 1]
        
        right_foot = len(total_shots[total_shots['isRightFooted'] == 1])
        left_foot = len(total_shots[total_shots['isLeftFooted'] == 1])
        head = len(total_shots[total_shots['isHead'] == 1])
        goals = len(total_shots[mask_goal])
        shots = len(total_shots[~mask_goal]) + goals
        xg = round(total_shots['xG'].sum(), 2)
        xg_op = round(op_shots['xG'].sum(), 2)
        xg_sp = round(non_op_shots['xG'].sum() - pk_shots['xG'].sum(), 2)
        xg_pk = round(pk_shots['xG'].sum(), 2)
        xg_shot = round(xg / shots, 2)
        np_xg = round(xg - xg_pk, 2)
        np_shots = round(shots - penalties_taken, 2)
        npxg_shot = round(np_xg / np_shots, 2)

        # add xG quality size
        ax.text(15, 127, 'Low-quality Chance', va='center', ha='center', color='w', fontsize=12, fontweight='bold', fontfamily=fontfamily)
        ax.text(65, 127, 'High-quality Chance', va='center', ha='center', color='w', fontsize=12, fontweight='bold', fontfamily=fontfamily)
        ax.text(35, 123, 'Goal', va='center', ha='center', color='w', fontsize=10, fontweight='bold', fontfamily=fontfamily)
        ax.text(45, 123, 'No Goal', va='center', ha='center', color='w', fontsize=10, fontweight='bold', fontfamily=fontfamily)

        ax.text(8, 77, 'Goals', va='center', ha='center', color='w', fontsize=13, fontweight='bold', fontfamily=fontfamily)
        ax.text(8, 74.5, goals, va='center', ha='center', color='#72bcd4', fontsize=12, fontweight='bold', fontfamily=fontfamily)        
        ax.text(40, 77, 'xG / npxG', va='center', ha='center', color='w', fontsize=13, fontweight='bold', fontfamily=fontfamily)
        ax.text(40, 74.5, f'{xg} / {round(xg-xg_pk,2)}', va='center', ha='center', color='#72bcd4', fontsize=12, fontweight='bold', fontfamily=fontfamily)
        ax.text(70, 77, 'npxG per Shot', va='center', ha='center', color='w', fontsize=13, fontweight='bold', fontfamily=fontfamily)
        ax.text(70, 74.5, f'{npxg_shot}', va='center', ha='center', color='#72bcd4', fontsize=12, fontweight='bold', fontfamily=fontfamily)
        ax.text(90, 120, 'Total Shots', va='center', ha='center', color='w', fontsize=13, fontweight='bold', fontfamily=fontfamily)
        ax.text(90, 117.5, f'{shots}', va='center', ha='center', color='#72bcd4', fontsize=12, fontweight='bold', fontfamily=fontfamily)
        ax.text(90, 109, 'PK Shots', va='center', ha='center', color='w', fontsize=13, fontweight='bold', fontfamily=fontfamily)
        ax.text(90, 106.5, f'{penalties_taken}', va='center', ha='center', color='#72bcd4', fontsize=12, fontweight='bold', fontfamily=fontfamily)     
        ax.text(90, 96.5, f'{right_foot}', va='center', ha='center', color='#72bcd4', fontsize=12, fontweight='bold', fontfamily=fontfamily)
        ax.text(90, 99, 'Right Foot', va='center', ha='center', color='w', fontsize=13, fontweight='bold', fontfamily=fontfamily)
        ax.text(90, 88.1, 'Left Foot', va='center', ha='center', color='w', fontsize=13, fontweight='bold', fontfamily=fontfamily)
        ax.text(90, 85.6, f'{left_foot}', va='center', ha='center', color='#72bcd4', fontsize=12, fontweight='bold', fontfamily=fontfamily)
        ax.text(90, 77, 'Head', va='center', ha='center', color='w', fontsize=13, fontweight='bold', fontfamily=fontfamily)
        ax.text(90, 74.5, f'{head}', va='center', ha='center', color='#72bcd4', fontsize=12, fontweight='bold', fontfamily=fontfamily)
        ax.text(1, 64, f'Created by @egudi_analysis\nExpected goals model trained on ~10k\nshots from the 2021/2022 EPL season\nExcludes Own Goals.', va='center', ha='left', color='w', fontsize=8, fontweight='bold', fontfamily=fontfamily)
            
        # Add xG quality size circles (corrected for aspect ratio)
        ax.add_patch(plt.Circle((30, 127), 0.25, color='w', transform=ax.transData))
        ax.add_patch(plt.Circle((35, 127), 0.5, color='w', transform=ax.transData))
        ax.add_patch(plt.Circle((40, 127), 0.75, color='w', transform=ax.transData))
        ax.add_patch(plt.Circle((45, 127), 1.00, color='w', transform=ax.transData))
        ax.add_patch(plt.Circle((50, 127), 1.25, color='w', transform=ax.transData))

        ax.add_patch(plt.Circle((40, 123), 0.9, color='gray', ec='w', lw=1.5, transform=ax.transData))
        ax.add_patch(plt.Circle((31, 123), 0.9, color='red',  ec='w', lw=1.5, alpha=0.6, transform=ax.transData))

        path = f'Logos/United SC Logo.png'
        ax_team = fig.add_axes([0.825,.695,0.125,0.125])
        ax_team.axis('off')
        im = plt.imread(path)
        ax_team.imshow(im);

        # save figure
        #fig.savefig(f'{players}_xG_shotmap.png', dpi=None, bbox_inches="tight")