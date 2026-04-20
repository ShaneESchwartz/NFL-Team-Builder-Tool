import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

from evaluate import evaluate_team_strict


# -----------------------
# LOAD DATA (same directory)
# -----------------------
av_team_strict = pd.read_pickle("av_team_strict.pkl")
playoff_means_strict = pd.read_pickle("playoff_means_strict.pkl")


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

        output.delete("1.0", tk.END)
        output.insert(tk.END, result.to_string())

    except Exception as e:
        messagebox.showerror("Error", str(e))


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
teams = sorted(av_team_strict["team"].unique())
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
# OUTPUT BOX
# -----------------------
output = tk.Text(root, height=25, width=80)
output.pack()


# -----------------------
# START APP
# -----------------------
root.mainloop()