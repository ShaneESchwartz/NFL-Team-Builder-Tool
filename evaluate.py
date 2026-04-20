import pandas as pd
import numpy as np

av_team_strict = pd.read_pickle("av_team_strict.pkl")
playoff_means_strict = pd.read_pickle("playoff_means_strict.pkl")
draft_pos_ratio = pd.read_pickle("draft_pos_ev_ratio.pkl").squeeze()

def draft_recommendation(ratio):
    if pd.isna(ratio):
        return "No data"

    if ratio <= 0.6:
        return "Extremely hard to draft (on average underperforms vs expectation by 40%+)"
    elif 0.6 < ratio <= .9:
        return "Somewhat Hard to draft (on average underperforms vs expectation by 10-40%)"

    elif 0.9 < ratio <= 1.1:
        return "Drafting is about average at this position (on average performs within 10% of expectiation)"

    elif  1.1 < ratio <= 1.4:
        return "Strong draft value (on average outperforms expectation by 10-40%)"

    elif ratio > 1.4:
        return "Extremely strong draft value (on average outperforms expectation by 40%+)"


def evaluate_team_strict(
    playoff_means_strict,
    team_data_strict,
    team=None,
    season=None,
    manual_input=None
):

    pos_cols = playoff_means_strict.index

    if manual_input is not None:
        input_vals = pd.Series(manual_input)

    elif team is not None and season is not None:
        row = team_data_strict[
            (team_data_strict["nfl"] == team) &
            (team_data_strict["season"] == season)
        ]

        if row.empty:
            raise ValueError("Team/season not found")

        input_vals = row[pos_cols].iloc[0]

    else:
        raise ValueError("Provide either (team & season) OR manual_input")

    input_vals = input_vals.reindex(pos_cols, fill_value=0)

    raw_delta = playoff_means_strict - input_vals
    pct_delta = raw_delta / playoff_means_strict.replace(0, np.nan)

    result = pd.DataFrame({
        "input_av": input_vals,
        "playoff_baseline": playoff_means_strict,
        "delta": raw_delta,
        "delta_pct": pct_delta * 100
    })

    
    result["draft_ev_ratio"] = draft_pos_ratio.reindex(result.index)
    result["draft_recommendation"] = result["draft_ev_ratio"].apply(draft_recommendation)

    return result.sort_values(by="delta", ascending=False)