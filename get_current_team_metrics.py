from nba_api.stats.endpoints import leaguegamelog
import pandas as pd


def get_league_game_log(season):
    # This function gets league game log data
    league_game_log = leaguegamelog.LeagueGameLog(
        season=season,
        season_type_all_star='Regular Season'
    )
    league_game_log_data = league_game_log.get_data_frames()[0]
    return league_game_log_data

"""
POSSIBLE STATS: ['SEASON_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_NAME', 
'GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'PTS', 'FGM', 'FGA', 
'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 
'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS']
"""

def elo_change(rating, opponent_rating, result):
    # Changes each team's elo based on the game's outcome
    K = 20
    expected_score = 1 / (1 + 10**((opponent_rating - rating) / 400))
    actual_score = 1 if result == 'W' else 0
    return K * (actual_score - expected_score)


def generate_metrics(season_data):
    # This function takes in data for a season and generates 3 columns:
    # ELO, the team's past 10 game plus-minus, and the home team.
     
    # Relevant data from season_data, slightly modified for easier feature engineering
    df = season_data[['TEAM_ABBREVIATION', 'MATCHUP', 'WL', 'GAME_DATE', 'PLUS_MINUS']]
    df = df.sort_values(by='GAME_DATE')
    df['MATCHUP'] = df['MATCHUP'].str[-3:]

    # Initializing data for columns
    df['NINE_GAME_PM'] = 0
    elo_ratings = {team: 1500 for team in set(df['TEAM_ABBREVIATION'])}
    team_elo_before = []
    opponent_elo_before = []

    for index, row in df.iterrows():
        team = row['TEAM_ABBREVIATION']
        opponent = row['MATCHUP']
        result = row['WL']
        current_date = row['GAME_DATE']

        # ELO
        team_elo_before.append(elo_ratings[team])
        opponent_elo_before.append(elo_ratings[opponent])
        team_elo_change = elo_change(elo_ratings[team], elo_ratings[opponent], result)
        opponent_elo_change = elo_change(elo_ratings[opponent], elo_ratings[team], 'L' if result == 'W' else 'W')
        elo_ratings[team] += team_elo_change
        elo_ratings[opponent] += opponent_elo_change

        # PAST 10 GAME PLUS MINUS
        team_rows = df[(df['TEAM_ABBREVIATION'] == team) & (df['GAME_DATE'] < current_date)].tail(9)
        rolling_sum = team_rows['PLUS_MINUS'].sum()
        df.at[index, 'NINE_GAME_PM'] = rolling_sum

    df['TEAM_ELO'] = team_elo_before
    df['OPPONENT_ELO'] = opponent_elo_before

    output = df[['TEAM_ABBREVIATION', 'TEAM_ELO', 'GAME_DATE', 'PLUS_MINUS', 'OPPONENT_ELO', 'WL', 'NINE_GAME_PM']]

    return output


def extract_current_metrics(X_test):
    unique_teams = X_test['TEAM_ABBREVIATION'].unique()
    team_elo = []
    team_10_game_pm = []
    game_date = []

    for team in unique_teams:
        team_data = X_test[X_test['TEAM_ABBREVIATION'] == team]
        last_game = team_data.iloc[-1]

        rating = last_game['TEAM_ELO']
        opponent_rating = last_game['OPPONENT_ELO']
        result = last_game['WL']
        team_elo_change = elo_change(rating, opponent_rating, result)
        team_elo.append(rating+team_elo_change)

        ten_game_pm = last_game['NINE_GAME_PM'] + last_game['PLUS_MINUS']
        team_10_game_pm.append(ten_game_pm)

        game_date.append(last_game['GAME_DATE'])

    team_metrics = pd.DataFrame({
        'Team': unique_teams,
        'GAME_DATE': game_date,
        'ELO': team_elo,
        'Last 10 Game Plus-Minus': team_10_game_pm
    })

    return team_metrics


def get_current_metrics():
    current_season_data = get_league_game_log('2023-24')
    current_data = generate_metrics(current_season_data)
    team_metrics = extract_current_metrics(current_data)
    team_metrics_elos = team_metrics.sort_values(by='ELO', ascending=False).reset_index(drop=True)
    current_metrics = team_metrics_elos[["Team", "ELO", "Last 10 Game Plus-Minus"]]
    rounded_metrics = current_metrics
    rounded_metrics.loc[:, 'ELO'] = rounded_metrics['ELO'].round(1)
    return current_metrics, rounded_metrics


if __name__ == "__main__":
    data = get_league_game_log('2023-24')
    [current_metrics, rounded_metrics] = get_current_metrics()