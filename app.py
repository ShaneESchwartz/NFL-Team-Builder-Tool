import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

from evaluate import evaluate_team_strict

# -----------------------
# LOAD DATA (same directory)
# -----------------------
av_team_strict = pd.read_pickle("av_team_strict.pkl")
playoff_means_strict = pd.read_pickle("playoff_means_strict.pkl")
draft_pos_ratio = pd.read_pickle("draft_pos_ev_ratio.pkl").squeeze()


# -----------------------
# MODE SELECTOR
# -----------------------



# -----------------------
# RUN FUNCTION
# -----------------------
def run_evaluation():
    mode = mode_var.get()

    try:
        if mode == "team":
            team = team_var.get()
            season_val = season_var.get()

            if not team:
                raise ValueError("Please select a team")

            if not season_val:
                raise ValueError("Please select a season")

            season = int(season_val)

            result = evaluate_team_strict(
                playoff_means_strict,
                av_team_strict,
                team=team,
                season=season
            )

        else:  # manual mode
            manual_input = {}

            for pos, entry in manual_entries.items():
                val = entry.get()
                manual_input[pos] = float(val) if val else 0.0

            result = evaluate_team_strict(
                playoff_means_strict,
                av_team_strict,
                manual_input=manual_input
            )

        # clear old rows
        for row in tree.get_children():
            tree.delete(row)

        # add EV ratio + recommendation
        result["draft_ev_ratio"] = draft_pos_ratio.reindex(result.index)
        result["draft_recommendation"] = result["draft_ev_ratio"].apply(draft_recommendation)

        # insert rows into table
        for idx, row in result.iterrows():
            tree.insert("", "end", values=[
                idx,
                round(row["input_av"], 2),
                round(row["playoff_baseline"], 2),
                round(row["delta"], 2),
                round(row["delta_pct"], 2),
                round(row["draft_ev_ratio"], 2) if pd.notna(row["draft_ev_ratio"]) else "",
                row["draft_recommendation"]
            ])

    except Exception as e:
        messagebox.showerror("Error", str(e))


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

# -----------------------
# GUI SETUP
# -----------------------
root = tk.Tk()
mode_var = tk.StringVar(value="team")
root.title("NFL Team Builder Tool")
root.geometry("700x700")


# -----------------------
# MODE DROPDOWN
# -----------------------
tk.Label(root, text="Mode").pack()
mode_dropdown = ttk.Combobox(root, textvariable=mode_var, values=["team", "manual"])
mode_dropdown.pack()


# -----------------------
# TEAM DROPDOWN
# -----------------------
teams = sorted(av_team_strict["nfl"].unique())
team_var = tk.StringVar()

tk.Label(root, text="Select Team").pack()
team_dropdown = ttk.Combobox(root, textvariable=team_var, values=teams)
team_dropdown.pack()


# -----------------------
# SEASON DROPDOWN
# -----------------------
seasons = sorted(av_team_strict["season"].unique())
season_var = tk.StringVar()

tk.Label(root, text="Select Season").pack()
season_dropdown = ttk.Combobox(root, textvariable=season_var, values=seasons)
season_dropdown.pack()


# -----------------------
# MANUAL INPUT FIELDS
# -----------------------
pos_cols = list(playoff_means_strict.index)

manual_entries = {}

frame = tk.Frame(root)
frame.pack()

tk.Label(frame, text="Manual Input (AV per position)").grid(row=0, column=0, columnspan=2)

for i, pos in enumerate(pos_cols):
    tk.Label(frame, text=pos).grid(row=i+1, column=0)
    entry = tk.Entry(frame)
    entry.grid(row=i+1, column=1)
    manual_entries[pos] = entry


# -----------------------
# RUN BUTTON
# -----------------------
tk.Button(root, text="Evaluate Team", command=run_evaluation).pack(pady=10)

# -----------------------
# OUTPUT TABLE (Treeview)
# -----------------------

columns = ["Position", "Input AV", "Playoff", "Delta", "Delta %", "EV Ratio", "Recommendation"]

tree = ttk.Treeview(root, columns=columns, show="headings")
tree.pack(fill="both", expand=True)

# for col in columns:
#     tree.heading(col, text=col)
#     tree.column(col, anchor="center", stretch=True)

# tree.column("Recommendation", width=500, anchor="w")
for col in columns:
    tree.heading(col, text=col)

# fixed widths (clean layout)
tree.column("Position", width=70, anchor="center", stretch=False)
tree.column("Input AV", width=80, anchor="center", stretch=False)
tree.column("Playoff", width=80, anchor="center", stretch=False)
tree.column("Delta", width=80, anchor="center", stretch=False)
tree.column("Delta %", width=80, anchor="center", stretch=False)
tree.column("EV Ratio", width=80, anchor="center", stretch=False)

# ONLY this column expands
tree.column("Recommendation", width=450, anchor="w", stretch=True)


# -----------------------
# START APP
# -----------------------
root.mainloop()