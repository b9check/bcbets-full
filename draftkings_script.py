from draftkings_class import DraftKings
import pandas as pd


def get_DK_moneylines():
    dk = DraftKings(league="NBA")
    pregame_bets_raw = dk.get_pregame_odds()
    teams1 = []
    teams2 = []
    team1_odds = []
    team2_odds = []
    for bet in pregame_bets_raw:
        started = bet['started']
        if not started:
            try:
                moneyline_outcomes = next(
                    market['outcomes']
                    for market in bet['markets']
                    if market['marketName'] == 'Moneyline'
                )
                team1 = moneyline_outcomes[0]['label'][0:3]
                team2 = moneyline_outcomes[1]['label'][0:3]
                if team1 == 'LA ':
                    team1 = moneyline_outcomes[0]['label'][0:4]
                if team2 == 'LA ':
                    team2 = moneyline_outcomes[1]['label'][0:4]
                teams1.append(team1)
                teams2.append(team2)
                team1_odds.append(moneyline_outcomes[0]['odds'])
                team2_odds.append(moneyline_outcomes[1]['odds'])
            except StopIteration:
                pass
            
    pregame_bets = pd.DataFrame({
        'Team 1': teams1, 
        'Team 2': teams2, 
        'Team 1 Odds': team1_odds, 
        'Team 2 Odds': team2_odds
        })
    return pregame_bets


if __name__ == "__main__":
    pregame_bets = get_DK_moneylines()
    print(pregame_bets)