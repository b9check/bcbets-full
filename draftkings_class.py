import requests
import json

id_dict = {"NHL": "42133", "NFL": "88808",
           "NBA": "42648", "England - Premier League": "40253"}


class DraftKings:
    def __init__(self, league="NBA"):
        """
        Initializes a class object
        Include more leagues simply by adding the league with its ID to id_dict above

        :league str: Name of the league, NHL by default
        """
        self.league = league
        self.pregame_url = f"https://sportsbook.draftkings.com//sites/US-SB/api/v5/eventgroups/{id_dict[self.league]}?format=json"
        self.uri = "wss://ws-draftkingseu.pusher.com/app/490c3809b82ef97880f2?protocol=7&client=js&version=7.3.0&flash=false"

    def get_event_ids(self) -> dict:
        """
        Finds all the games & their event_ids for the given league

        :rtype: dict
        """
        event_ids = {}
        response = requests.get(self.pregame_url).json()
        for event in response['eventGroup']['events']:
            event_ids[event['name']] = event['eventId']
        return event_ids

    def get_pregame_odds(self) -> list:
        """
        Collects the market odds for the main markets [the ones listed at the league's main url] for the league

        E.g. for the NHL, those are Puck Line, Total and Moneyline

        Returns a list with one object for each game

        :rtype: list
        """
        # List that will contain dicts [one for each game]
        games_list = []

        # Requests the content from DK's API, loops through the different games & collects all the material deemed relevant
        response = requests.get(self.pregame_url).json()
        games = response['eventGroup']['offerCategories'][0]['offerSubcategoryDescriptors'][0]['offerSubcategory']['offers']
        
        for index, game in enumerate(games, start=0):
            # List that will contain dicts [one for each market]
            market_list = []
            # Check if game has started
            state = response['eventGroup']['events'][index]['eventStatus']['state']
            if state == 'STARTED':
                started = True
            else:
                started = False

            for market in game:
                try:
                    market_name = market['label']
                    if market_name == "Moneyline":
                        home_team = market['outcomes'][1]['label']
                        away_team = market['outcomes'][0]['label']
                    if market_name == 'eventStatus':
                        print('hi')
                    # List that will contain dicts [one for each outcome]
                    outcome_list = []
                    for outcome in market['outcomes']:
                        try:
                            # if there's a line it should be included in the outcome description
                            line = outcome['line']
                            outcome_label = outcome['label'] + " " + str(line)
                        except:
                            outcome_label = outcome['label']
                        outcome_odds = outcome['oddsAmerican']
                        outcome_list.append(
                            {"label": outcome_label, "odds": outcome_odds})
                    market_list.append(
                        {"marketName": market_name, "outcomes": outcome_list})
                except Exception as e:
                    if self.league == "NBA" and "label" in str(e):
                        # odds for NBA totals are not available as early as the other markets for
                        # games a few days away, thus raises a KeyError: 'label'
                        # in this case we simply ignore the error and continue with the next market
                        continue
                    else:
                        # if there was another problem with a specific market, print the error and
                        # continue with the next one...
                        #print_exc()
                        print()
                        continue
            try: 
                games_list.append(
                    {"game": f"{home_team} v {away_team}", "started": started, "markets": market_list})

            except:
                pass
        return games_list