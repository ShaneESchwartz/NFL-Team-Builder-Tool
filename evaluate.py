import pandas as pd
import numpy as np

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
            (team_data_strict["team"] == team) &
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

    return result.sort_values(by="delta", ascending=False)