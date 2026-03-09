import pandas as pd
import ast
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
import numpy as np
from matplotlib import cm
from matplotlib.colors import Normalize
import numpy as np
from scipy.interpolate import Rbf
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MaxNLocator



import numpy as np

def load_iterations_csv(path):
    with open(path, "r") as f:
        lines = f.readlines()

    # Find header
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("iteration,"):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError(f"Could not find iteration header in {path}")

    df = pd.read_csv(path, skiprows=header_idx)

    # Remove the "actual_initial_state" row
    df = df[pd.to_numeric(df["iteration"], errors="coerce").notna()]
    df["iteration"] = df["iteration"].astype(int)

    return df







def parse_solution(sol_str):
    if pd.isna(sol_str):
        return None
    try:
        return ast.literal_eval(sol_str)
    except Exception:
        return None

# -----------------------------
# Load all CSV files
# -----------------------------
folder = Path(r"C:\Users\reddr\Documents\Scandiatransplant_modelling\metaheuristic\results\V2")
csv_files = list(folder.glob("*.csv"))

all_dfs = []

for file in csv_files:
    df = load_iterations_csv(file)
    df["solution_parsed"] = df["current_solution"].apply(parse_solution)
    df = df.dropna(subset=["solution_parsed"])

    df["x"] = df["solution_parsed"].apply(lambda s: s[0])
    df["y"] = df["solution_parsed"].apply(lambda s: s[1])
    

    df["run"] = file.stem
    all_dfs.append(df)

import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
import matplotlib.cm as cm


# Combine all runs
big_df = pd.concat(all_dfs, ignore_index=True)





# Best point
best_idx = big_df["current_eval"].idxmax()
best_point = big_df.loc[best_idx]

# Tied points
big_df["eval_3dp"] = big_df["current_eval"].round(4)
best_3dp = best_point["current_eval"].round(4)
tied_points = big_df[(big_df["eval_3dp"] == best_3dp) & (big_df.index != best_idx)]

# Color normalization (more sensitive at high values)

norm = PowerNorm(
    gamma=12,   # try 2–3 for strong high-value sensitivity
    vmin=big_df["current_eval"].min(),
    vmax=big_df["current_eval"].max()
)

cmap = cm.turbo

# ---- Single plot ----
fig, ax = plt.subplots(figsize=(10, 8))

sc = ax.scatter(
    big_df["x"], big_df["y"],
    c=cmap(norm(big_df["current_eval"])),
    s=20
)

# tied points
ax.scatter(
    tied_points["x"], tied_points["y"],
    color="grey", s=60, edgecolor="black"
)
import numpy as np

# Fit a line to the tied points
x_tied = tied_points["x"].values
y_tied = tied_points["y"].values

# Linear regression: y = a*x + b
a, b = np.polyfit(x_tied, y_tied, 1)

# Create line for plotting
x_line = np.linspace(big_df["x"].min(), big_df["x"].max(), 200)
y_line = a * x_line + b

# Plot the fitted line
ax.plot(x_line, y_line, color="black", linewidth=2, linestyle="--")
# Edge lines for high-value region

# best point
ax.scatter(
    best_point["x"], best_point["y"],
    color="black", s=100, edgecolor="black"
)

ax.set_xlabel("Mismatch weight")
ax.set_ylabel("Distance weight")
ax.set_title("Mismatch vs Distance")

# Colorbar (now correctly attached)
mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
mappable.set_array([])
cbar = fig.colorbar(mappable, ax=ax, shrink=0.8)
cbar.set_label("current_eval")
low_cut = 1.54
vmin = big_df["current_eval"].min()
vmax = big_df["current_eval"].max()

# Generate ticks only above 1.53, clustered toward the top
t = np.linspace(0, 1, 12) ** 0.5     # exponent < 1 clusters ticks near vmax
ticks = low_cut + t * (vmax - low_cut)

cbar.set_ticks(ticks)
cbar.set_ticklabels([f"{x:.3f}" for x in ticks])

plt.show()
