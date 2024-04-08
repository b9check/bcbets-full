from get_current_team_metrics import get_current_metrics
from compare_odds import get_DK_bets_analysis
import pandas as pd
import os

file_path = os.getcwd() + '\DK_analysis.csv'
DK_analysis = get_DK_bets_analysis()

DK_analysis.to_csv(file_path, index=False)
