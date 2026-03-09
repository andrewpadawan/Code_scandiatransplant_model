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


def fit_rbf_surface(X, Y, Z, grid_size=40, function="thin_plate", smooth=0):
    """
    Fit a non-parametric surface z = f(x, y) using RBF interpolation.

    Parameters:
        X, Y, Z : 1D arrays of point coordinates
        grid_size : resolution of the plotted surface
        function : RBF kernel ("thin_plate", "multiquadric", "gaussian", etc.)
        smooth : smoothing factor (0 = exact interpolation)

    Returns:
        xx, yy, zz : meshgrid surface arrays
        rbf_model : the fitted RBF model
    """

    # Build RBF model
    rbf = Rbf(X, Y, Z, function=function, smooth=smooth)

    # Create grid for visualization
    xx, yy = np.meshgrid(
        np.linspace(X.min(), X.max(), grid_size),
        np.linspace(Y.min(), Y.max(), grid_size)
    )
    zz = rbf(xx, yy)

    return xx, yy, zz, rbf




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
folder = Path(r"C:\Users\reddr\Documents\Scandiatransplant_modelling\metaheuristic\results")
csv_files = list(folder.glob("*.csv"))

all_dfs = []

for file in csv_files:
    df = load_iterations_csv(file)
    df["solution_parsed"] = df["current_solution"].apply(parse_solution)
    df = df.dropna(subset=["solution_parsed"])

    df["x"] = df["solution_parsed"].apply(lambda s: s[0])
    df["y"] = df["solution_parsed"].apply(lambda s: s[1])
    df["z"] = df["solution_parsed"].apply(lambda s: s[2])

    df["run"] = file.stem
    all_dfs.append(df)

# Combine all runs
big_df = pd.concat(all_dfs, ignore_index=True)

# -----------------------------
# Global color normalization
# -----------------------------
norm = Normalize(
    vmin=big_df["current_eval"].min(),
    vmax=big_df["current_eval"].max()
)
cmap = cm.turbo

# -----------------------------
# Best point (highest eval)
# -----------------------------
best_idx = big_df["current_eval"].idxmax()
best_point = big_df.loc[best_idx]

# -----------------------------
# Find tied points (4 decimals)
# -----------------------------
big_df["eval_3dp"] = big_df["current_eval"].round(4)
best_3dp = best_point["current_eval"].round(4)

tied_points = big_df[big_df["eval_3dp"] == best_3dp]
tied_points = tied_points[tied_points.index != best_idx]   # remove the single best

# -----------------------------
# Fit 3D planes (used in 3D + Mismatch–Equity)
# -----------------------------
high_df = big_df[big_df["current_eval"] >= 1.745].copy()

# Bin x and y into a grid
xbins = np.linspace(big_df["x"].min(), big_df["x"].max(), 12)
ybins = np.linspace(big_df["y"].min(), big_df["y"].max(), 12)

high_df["xbin"] = np.digitize(high_df["x"], xbins)
high_df["ybin"] = np.digitize(high_df["y"], ybins)

# Compute upper and lower envelopes
upper = high_df.groupby(["xbin", "ybin"])["z"].max().dropna()
lower = high_df.groupby(["xbin", "ybin"])["z"].min().dropna()

# Convert bin indices to coordinates
x_centers = (xbins[:-1] + xbins[1:]) / 2
y_centers = (ybins[:-1] + ybins[1:]) / 2

upper_points = []
lower_points = []

for (xb, yb), zval in upper.items():
    if 1 <= xb <= len(x_centers) and 1 <= yb <= len(y_centers):
        upper_points.append([x_centers[xb-1], y_centers[yb-1], zval])

for (xb, yb), zval in lower.items():
    if 1 <= xb <= len(x_centers) and 1 <= yb <= len(y_centers):
        lower_points.append([x_centers[xb-1], y_centers[yb-1], zval])

upper_points = np.array(upper_points)
lower_points = np.array(lower_points)

def fit_plane(points):
    X = points[:, :2]
    X = np.column_stack([X, np.ones(len(X))])
    z = points[:, 2]
    a, b, c = np.linalg.lstsq(X, z, rcond=None)[0]
    return a, b, c

a_up, b_up, c_up = fit_plane(upper_points)
a_low, b_low, c_low = fit_plane(lower_points)

# -----------------------------
# 2×2 Figure
# -----------------------------
fig = plt.figure(figsize=(14, 12))

# ---- 1. Mismatch vs Distance (FIXED, no planes) ----
ax1 = fig.add_subplot(221)
df_sorted_equity = big_df.sort_values("z")

ax1.scatter(
    df_sorted_equity["x"], df_sorted_equity["y"],
    c=cmap(norm(df_sorted_equity["current_eval"])),
    s=20
)

# tied points = light pink
ax1.scatter(tied_points["x"], tied_points["y"], color="grey", s=60, edgecolor="black")

# best point = black
ax1.scatter(best_point["x"], best_point["y"], color="black", s=100, edgecolor="black")

ax1.set_xlabel("Mismatch weight")
ax1.set_ylabel("Distance weight")
ax1.set_title("Mismatch vs Distance")

# ---- 2. Mismatch vs Equity (uses planes) ----
ax2 = fig.add_subplot(222)

# Base scatter
ax2.scatter(
    big_df["x"], big_df["z"],
    c=cmap(norm(big_df["current_eval"])),
    s=20
)

# Tied points (light pink)
ax2.scatter(
    tied_points["x"], tied_points["z"],
    color="grey", s=60, edgecolor="black"
)

# Best point (black)
ax2.scatter(
    best_point["x"], best_point["z"],
    color="black", s=100, edgecolor="black"
)

# Project the SAME 3D planes into this 2D plot
y_fixed = big_df["y"].mean()
x_line = np.linspace(big_df["x"].min(), big_df["x"].max(), 200)

z_upper_line = a_up * x_line + b_up * y_fixed + c_up
z_lower_line = a_low * x_line + b_low * y_fixed + c_low

ax2.plot(x_line, z_upper_line, color="#003f8c", linewidth=2)
ax2.plot(x_line, z_lower_line, color="#003f8c", linewidth=2)

ax2.set_xlabel("Mismatch weight")
ax2.set_ylabel("Equity weight")
ax2.set_title("Mismatch vs Equity")

# ---- 3. Distance vs Equity (y vs z) ----
ax3 = fig.add_subplot(223)

ax3.scatter(
    big_df["y"], big_df["z"],
    c=cmap(norm(big_df["current_eval"])),
    s=20
)

# Tied points
ax3.scatter(
    tied_points["y"], tied_points["z"],
    color="grey", s=60, edgecolor="black"
)

# Best point
ax3.scatter(
    best_point["y"], best_point["z"],
    color="black", s=100, edgecolor="black"
)

ax3.set_xlabel("Distance weight")
ax3.set_ylabel("Equity weight")
ax3.set_title("Distance vs Weight")



# ---- 4. 3D plot ----
ax4 = fig.add_subplot(224, projection="3d")
ax4.scatter(
    big_df["x"], big_df["y"], big_df["z"],
    c=cmap(norm(big_df["current_eval"])),
    s=25
)

# tied points = light pink
ax4.scatter(
    tied_points["x"], tied_points["y"], tied_points["z"],
    color="grey", s=120, edgecolor="black"
)

# best point = black
ax4.scatter(
    best_point["x"], best_point["y"], best_point["z"],
    color="black", s=150, edgecolor="black"
)

# Planes in 3D
xx, yy = np.meshgrid(
    np.linspace(big_df["x"].min(), big_df["x"].max(), 20),
    np.linspace(big_df["y"].min(), big_df["y"].max(), 20)
)

zz_up = a_up * xx + b_up * yy + c_up
zz_low = a_low * xx + b_low * yy + c_low

# Plot planes (now less translucent)
ax4.plot_surface(
    xx, yy, zz_up,
    alpha=0.50,          # less translucent
    color="#003f8c"      # dark blue
)

ax4.plot_surface(
    xx, yy, zz_low,
    alpha=0.50,          # less translucent
    color="#003f8c"
)


ax4.set_xlabel("Mismatch weight")
ax4.set_ylabel("Distance weight")
ax4.set_zlabel("Equity weight")
ax4.set_title("3D View")

# enlarge 3D plot
pos = ax4.get_position()
ax4.set_position([pos.x0 - 0.05, pos.y0 - 0.05, pos.width + 0.10, pos.height + 0.10])

# colorbar
plt.subplots_adjust(left=0.15)
mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
mappable.set_array([])

cbar_ax = fig.add_axes([0.05, 0.15, 0.02, 0.7])
cbar = fig.colorbar(mappable, cax=cbar_ax)
cbar.set_label("current_eval")

plt.show()
##########only 3d plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

# Base scatter
ax.scatter(
    big_df["x"], big_df["y"], big_df["z"],
    c=cmap(norm(big_df["current_eval"])),
    s=25
)

# Tied points (light pink)
ax.scatter(
    tied_points["x"], tied_points["y"], tied_points["z"],
    color="grey", s=120, edgecolor="black"
)

# Best point (black)
ax.scatter(
    best_point["x"], best_point["y"], best_point["z"],
    color="black", s=150, edgecolor="black"
)

# Create meshgrid for the planes
xx, yy = np.meshgrid(
    np.linspace(big_df["x"].min(), big_df["x"].max(), 20),
    np.linspace(big_df["y"].min(), big_df["y"].max(), 20)
)

zz_up = a_up * xx + b_up * yy + c_up
zz_low = a_low * xx + b_low * yy + c_low

# Upper plane
ax.plot_surface(
    xx, yy, zz_up,
    alpha=0.50,
    color="#003f8c"
)

# Lower plane
ax.plot_surface(
    xx, yy, zz_low,
    alpha=0.50,
    color="#003f8c"
)

# Labels and title
ax.set_xlabel("Mismatch weight")
ax.set_ylabel("Distance weight")
ax.set_zlabel("Equity weight")
ax.set_title("3D View")

# Optional: enlarge the 3D plot
pos = ax.get_position()
ax.set_position([pos.x0 - 0.05, pos.y0 - 0.05, pos.width + 0.10, pos.height + 0.10])

# Colorbar
mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
mappable.set_array([])
cbar = fig.colorbar(mappable, ax=ax, shrink=0.7)

cbar.set_label("current_eval")

plt.show()

# ============================================================
# SECOND FIGURE: Only best point + tied points
# ============================================================

fig2 = plt.figure(figsize=(14, 12))
# For all three subplots:







# ---- 1. Mismatch vs Distance ----
ax1b = fig2.add_subplot(221)

# tied points (light pink)
ax1b.scatter(tied_points["x"], tied_points["y"], color="grey", s=80, edgecolor="black")

# best point (black)
ax1b.scatter(best_point["x"], best_point["y"], color="black", s=140, edgecolor="black")

ax1b.set_xlabel("Mismatch weight")
ax1b.set_ylabel("Distance weight")
ax1b.set_title("Mismatch vs Distance (Best + Tied Only)")

ax1b.set_xlim(0, 1000)
ax1b.set_ylim(0, 1000)

# ---- 2. Mismatch vs Equity ----
ax2b = fig2.add_subplot(222)

ax2b.scatter(tied_points["x"], tied_points["z"], color="grey", s=80, edgecolor="black")
ax2b.scatter(best_point["x"], best_point["z"], color="black", s=140, edgecolor="black")

ax2b.set_xlabel("Mismatch weight")
ax2b.set_ylabel("Equity weight")
ax2b.set_title("Mismatch vs Equity (Best + Tied Only)")
ax2b.set_xlim(0, 1000)
ax2b.set_ylim(0, 1000)
# ---- 3. Distance vs Equity ----
ax3b = fig2.add_subplot(223)

ax3b.scatter(tied_points["y"], tied_points["z"], color="grey", s=80, edgecolor="black")
ax3b.scatter(best_point["y"], best_point["z"], color="black", s=140, edgecolor="black")

ax3b.set_xlabel("Distance weight")
ax3b.set_ylabel("Equity weight")
ax3b.set_title("Distance vs Equity (Best + Tied Only)")
ax3b.set_xlim(0, 1000)
ax3b.set_ylim(0, 1000)
"""
# ---- 4. 3D plot ----
ax4b = fig2.add_subplot(224, projection="3d")

# Scatter points
ax4b.scatter(
    tied_points["x"], tied_points["y"], tied_points["z"],
    color="grey", s=140, edgecolor="black"
)

ax4b.scatter(
    best_point["x"], best_point["y"], best_point["z"],
    color="black", s=200, edgecolor="black"
)

# === SAME PLANES, LESS TRANSLUCENT ===
xx, yy = np.meshgrid(
    np.linspace(big_df["x"].min(), big_df["x"].max(), 20),
    np.linspace(big_df["y"].min(), big_df["y"].max(), 20)
)

zz_up = a_up * xx + b_up * yy + c_up
zz_low = a_low * xx + b_low * yy + c_low

ax4b.plot_surface(
    xx, yy, zz_up,
    alpha=0.50,
    color="#003f8c"
)

ax4b.plot_surface(
    xx, yy, zz_low,
    alpha=0.50,
    color="#003f8c"
)

ax4b.set_xlabel("Mismatch weight")
ax4b.set_ylabel("Distance weight")
ax4b.set_zlabel("Equity weight")
ax4b.set_title("3D View (Best + Tied Only)")
"""

# ---- 4. 3D plot ----
ax4b = fig2.add_subplot(224, projection="3d")

# Scatter points
ax4b.scatter(
    tied_points["x"], tied_points["y"], tied_points["z"],
    color="grey", s=140, edgecolor="black"
)

ax4b.scatter(
    best_point["x"], best_point["y"], best_point["z"],
    color="black", s=200, edgecolor="black"
)
"""
# ============================================================
# FIT PLANE THROUGH BEST POINT + TWO BEST TIED POINTS
# ============================================================

# ----------------------------------------------------------
# Example usage with your best + tied points
# ----------------------------------------------------------

# Collect your points
X = np.array(tied_points["x"].tolist() + [best_point["x"]])
Y = np.array(tied_points["y"].tolist() + [best_point["y"]])
Z = np.array(tied_points["z"].tolist() + [best_point["z"]])

# Fit surface
xx, yy, zz, rbf_model = fit_rbf_surface(X, Y, Z, function="thin_plate", smooth=0)

# Plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

# Scatter original points
ax.scatter(X, Y, Z, color="red", s=60, edgecolor="black")

# Plot surface
ax.plot_surface(xx, yy, zz, alpha=0.5, color="gold", edgecolor="none")"""

ax.set_xlabel("Mismatch weight")
ax.set_ylabel("Distance weight")
ax.set_zlabel("Equity weight")
ax.set_title("Non-parametric RBF Surface Fit")
ax4b.set_xlim(0, 1000)
ax4b.set_ylim(0, 1000)
ax4b.set_zlim(0, 1000)

plt.show()
