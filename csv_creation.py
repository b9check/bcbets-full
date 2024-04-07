from get_current_team_metrics import get_current_metrics
from compare_odds import get_DK_bets_analysis
import pandas as pd
import os

current_directory = os.getcwd()
relative_path = '\\DK_analysis.csv'
file_path = os.path.join(current_directory, relative_path)

DK_analysis = get_DK_bets_analysis()

DK_analysis.to_csv('C:\\Users\\brian\\OneDrive\\Desktop\\SportsAnalytics\\NBAWins\\Website\\tables\\DK_analysis.csv', index=False)
