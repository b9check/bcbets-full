# BC Bets Full

BC Bets Full is an automated NBA betting analysis tool that combines real-time betting odds, advanced team performance metrics, and machine learning predictions to identify value bets. The project gathers pregame moneylines from DraftKings, computes current team metrics (such as Elo ratings and recent performance via plus-minus), and uses a pre-trained model to predict “fair” winning percentages. By comparing these predictions with the odds implied by the moneylines, the tool helps pinpoint potentially profitable betting opportunities.

---

## Project Overview

This repository is organized into several scripts, each responsible for a distinct part of the overall workflow:

1. **DraftKings Odds Retrieval:**
   - **`draftkings_class.py`**: Defines a `DraftKings` class to interface with DraftKings’ pregame API. It fetches event IDs and market odds for the specified league (currently NBA by default).
   - **`draftkings_script.py`**: Utilizes the `DraftKings` class to extract moneyline odds for NBA games that have not yet started. It cleans and structures the odds data into a Pandas DataFrame for further analysis.

2. **Team Metrics Calculation:**
   - **`get_current_team_metrics.py`**: Uses the `nba_api` to pull NBA game logs for a given season (set to "2023-24"). It computes key performance metrics for each team:
     - **Elo Rating:** Updated for every game using a standard Elo change formula.
     - **Rolling Plus-Minus:** Aggregates a team’s performance over the last 10 games.
     
     The output is a DataFrame with current team metrics that can be used for comparison against betting odds.

3. **Betting Analysis & Comparison:**
   - **`compare_odds.py`**: This is the heart of the analysis. It performs the following tasks:
     - Loads the current moneyline odds from DraftKings (via `draftkings_script.py`).
     - Retrieves up-to-date team metrics from `get_current_team_metrics.py`.
     - Uses a pre-trained machine learning model (loaded from `trained_model.joblib` with its corresponding `scaler.joblib`) to predict the “fair” winning percentage for each team based on features like the Elo difference and recent plus-minus.
     - Converts both the model’s predicted winning percentages and the odds-implied winning percentages into comparable metrics.
     - Calculates the difference (confidence level) between the fair and current odds, then designates the team with the greater difference as the “best bet” for that matchup.
     - Outputs a summary table listing each matchup, current odds, the best bet, and the confidence level.

4. **CSV Report Generation:**
   - **`csv_creation.py`**: Automates the export of key results by:
     - Running the betting analysis from `compare_odds.py` to produce a summary DataFrame.
     - Retrieving the latest team metrics.
     - Saving both the betting analysis and the team metrics into CSV files (`DK_analysis.csv` and `rounded_metrics.csv`) in the current working directory.

5. **Supporting Files & Templates:**
   - **`templates/`**: Contains HTML templates (if you choose to build a web-based presentation) to format and display the analysis results.
   - **`.gitignore`**: Standard file to exclude unnecessary files from version control.
   - **Model Files:**
     - **`trained_model.joblib`** and **`scaler.joblib`** are pre-trained objects (a machine learning model and a scaler) that are loaded in `compare_odds.py` to predict fair winning percentages.

---

## Workflow Summary

1. **Data Retrieval:**
   - The tool first gathers pregame moneylines from DraftKings using the API (via `draftkings_class.py` and `draftkings_script.py`).
   - Simultaneously, it collects historical NBA game data using the `nba_api` in `get_current_team_metrics.py` and computes updated performance metrics (Elo ratings and rolling plus-minus).

2. **Fair Odds Calculation:**
   - In `compare_odds.py`, these team metrics are fed into a pre-trained machine learning model to estimate the true (fair) winning probabilities for each team.

3. **Odds Comparison:**
   - The script compares the fair winning percentages with those implied by the current betting odds.
   - It then computes the difference (confidence level) to determine which bet is most favorable.

4. **Reporting:**
   - A summary DataFrame is produced, listing matchups, current odds, the recommended (best) bet, and the confidence level.
   - Optionally, `csv_creation.py` can be run to export this analysis along with the team metrics into CSV files.

---

## Installation & Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/b9check/bcbets-full.git
   cd bcbets-full
