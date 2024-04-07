from draftkings_script import get_DK_moneylines
from get_current_team_metrics import get_current_metrics
from joblib import load
import pandas as pd
from math import *


# For converting DraftKings team abbreviations to NBA API abbreviations
DK_to_API = {'MIL': 'MIL', 'PHI': 'PHI', 'LA L': 'LAL', 'PHO': 'PHX', 'DAL': 'DAL', 'IND': 'IND',
             'CLE': 'CLE', 'WAS': 'WAS', 'DEN': 'DEN', 'GS ': 'GSW', 'OKC': 'OKC', 'HOU': 'HOU',
             'CHI': 'CHI', 'NO ': 'NOP', 'ORL': 'ORL', 'ATL': 'ATL', 'SA ': 'SAS', 'UTA': 'UTA',
             'CHA': 'CHA', 'POR': 'POR', 'SAC': 'SAC', 'LA C': 'LAC', 'MIA': 'MIA', 'MEM': 'MEM',
             'TOR': 'TOR', 'DET': 'DET', 'NY ': 'NYK', 'BKN': 'BKN', 'MIN': 'MIN', 'BOS': 'BOS'}


# Converts a winning percentage to a fair line
def WP_to_line(win_percentage):
    Ratio = 1/win_percentage - 1
    Fair_Line = 0
    if Ratio <= 1:
        Fair_Line = "-"+str(int(100/Ratio))
    else:
        Fair_Line = "+"+str(int(100*Ratio))
    return Fair_Line


# Converts line to a winning percentage
def line_to_WP(line):
    if line[0] == "+":
        ratio = int(line[1:])/100
    else:
        ratio = 100/abs(int(line))
    WP = 1/(ratio+1)
    return WP


# Get difference between two lines
def get_line_diffs(current_lines, fair_lines):
    diffs = []
    for current_line, fair_line in zip(current_lines, fair_lines):
        current_line = int(current_line)
        fair_line = int(fair_line)
        if (current_line > 0 and fair_line > 0) or (current_line < 0 and fair_line < 0):
            diff = current_line-fair_line
        elif current_line > 0 and fair_line < 0:
            diff = (current_line-100)+abs(fair_line+100)
        else:
            diff = -(abs(current_line+100)+(fair_line-100))
        diffs.append(diff)
    return diffs


# Calculates difference from fair vs. current winning percentages
def get_wp_diffs(lines, fair_wps):
    diffs = []
    for line, fair_wp in zip(lines, fair_wps):
        current_wp = line_to_WP(line)
        diffs.append(fair_wp - current_wp)
    return diffs


def get_DK_bets_analysis():
    # Load DK lines and current metrics
    bets = get_DK_moneylines()
    [current_metrics, rounded_metrics] = get_current_metrics()
    model = load('trained_model.joblib')
    scaler = load('scaler.joblib')
    fair_wps1 = []
    fair_wps2 = []

    # Caluculate fair lines and winning percentages for all bets
    for index, bet in bets.iterrows():
        team1 = DK_to_API[bet['Team 1']]
        team2 = DK_to_API[bet['Team 2']]
        team1_data = current_metrics[current_metrics['Team'] == team1]
        team2_data = current_metrics[current_metrics['Team'] == team2]
        elo1 = team1_data['ELO'].values[0]  # Assuming there's only one row for the team
        pm1 = team1_data['Last 10 Game Plus-Minus'].values[0]
        elo2 = team2_data['ELO'].values[0]  # Assuming there's only one row for the team
        pm2 = team2_data['Last 10 Game Plus-Minus'].values[0]
        x_data1 = pd.DataFrame({
            'ELO_DIFFERENCE': [elo1-elo2],
            'TEN_GAME_PM_DIFFERENCE': [pm1-pm2], 
            'HOME_AWAY': [0]
        })

        x_data2 = pd.DataFrame({
            'ELO_DIFFERENCE': [elo2-elo1],
            'TEN_GAME_PM_DIFFERENCE': [pm2-pm1], 
            'HOME_AWAY': [1]
        })

        y_pred1 = model.predict(scaler.transform(x_data1))[0]
        y_pred2 = model.predict(scaler.transform(x_data2))[0]
        fair_wps1.append(y_pred1)
        fair_wps2.append(y_pred2)

    # Calculate difference between current and fair lines/winning percentages
    wp_diffs1 = get_wp_diffs(bets['Team 1 Odds'], fair_wps1)
    wp_diffs2 = get_wp_diffs(bets['Team 2 Odds'], fair_wps2)

    # Calculate better bet and confidence
    better_bets = ['1' if diff1 >= diff2 else '2' for diff1, diff2 in zip(wp_diffs1, wp_diffs2)]
    winning_bets = []
    winning_bet_diffs = []
    abs_diff = []
    for index, bet in enumerate(better_bets):
        team = bets['Team '+bet].iloc[index]
        odds = bets['Team '+bet+' Odds'].iloc[index]
        winning_bet = team + ' ' + odds
        winning_bets.append(winning_bet)
        win_diff = wp_diffs1[index] if bet == '1' else wp_diffs2[index]
        winning_bet_diffs.append(win_diff)
        
    # Create summary table
    Summary = pd.DataFrame({
        'Matchup': bets['Team 1'].astype(str) + ' @ ' + bets['Team 2'].astype(str),
        'Line 1': bets['Team 1'].astype(str) + ' ' + bets['Team 1 Odds'].astype(str),
        #'WP 1': fair_wps1,
        #'WP Diff 1': wp_diffs1,
        'Line 2': bets['Team 2'].astype(str) + ' ' + bets['Team 2 Odds'].astype(str),
        #'WP 2': fair_wps2,
        #'WP Diff 2': wp_diffs2,
        'Best Bet': winning_bets,
        'Confidence': winning_bet_diffs,
    })

    return Summary


if __name__ == "__main__":
    Summary = get_DK_bets_analysis()
    print(Summary)


