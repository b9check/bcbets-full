from get_current_team_metrics import get_current_metrics
from compare_odds import get_DK_bets_analysis
import pandas as pd
import os

DK_analysis = get_DK_bets_analysis()
DK_path = os.getcwd() + '\DK_analysis.csv'

[current_metrics, rounded_metrics] = get_current_metrics()
metrics_path = os.getcwd() + '\rounded_metrics.csv'

DK_analysis.to_csv(DK_path, index=False)
rounded_metrics.to_csv(metrics_path, index=False)
