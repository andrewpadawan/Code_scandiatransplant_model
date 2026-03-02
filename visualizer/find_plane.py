from metaheuristic.objective_function import objective_aprox
import numpy as np

import pandas as pd
import ast
import matplotlib.pyplot as plt

from pathlib import Path

from matplotlib import cm
from matplotlib.colors import Normalize

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import Rbf
import json







# ============================================================
# LOAD CSVs
# ============================================================

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


# ============================================================
# FIND BEST + TIED POINTS
# ============================================================

best_idx = big_df["current_eval"].idxmax()
best_point = big_df.loc[best_idx]

big_df["eval_4dp"] = big_df["current_eval"].round(4)
best_4dp = best_point["current_eval"].round(4)

tied_points = big_df[big_df["eval_4dp"] == best_4dp]
tied_points = tied_points[tied_points.index != best_idx]

print("Best point:")
print(best_point[["x", "y", "z", "current_eval"]])

print("\nTied points:")
print(tied_points[["x", "y", "z", "current_eval"]])


# ============================================================
# BUILD RBF SURFACE
# ============================================================

def build_rbf_surface(X, Y, Z, function="thin_plate", smooth=0):
    rbf = Rbf(X, Y, Z, function=function, smooth=smooth)

    centers_x = rbf.xi[0]
    centers_y = rbf.xi[1]
    weights = rbf.nodes
    func = rbf.function
    eps = rbf.epsilon

    def phi(r):
        if func == "thin_plate":
            return np.where(r > 0, r**2 * np.log(r), 0.0)
        elif func == "multiquadric":
            return np.sqrt((1/eps**2) + r**2)
        elif func == "inverse_multiquadric":
            return 1.0 / np.sqrt((1/eps**2) + r**2)
        elif func == "gaussian":
            return np.exp(-(eps*r)**2)
        else:
            raise ValueError(f"Unsupported RBF kernel: {func}")

    def surface(x, y):
        x = np.asarray(x)
        y = np.asarray(y)
        z = np.zeros_like(x, dtype=float)
        for cx, cy, w in zip(centers_x, centers_y, weights):
            r = np.sqrt((x - cx)**2 + (y - cy)**2)
            z += w * phi(r)
        return z

    return surface, rbf



# Build RBF surface from best + tied points
X = np.array(tied_points["x"].tolist() + [best_point["x"]])
Y = np.array(tied_points["y"].tolist() + [best_point["y"]])
Z = np.array(tied_points["z"].tolist() + [best_point["z"]])

rbf_surface, rbf_model = build_rbf_surface(X, Y, Z, function="thin_plate", smooth=0)


# ============================================================
# SAMPLE AND PLOT RBF SURFACE
# ============================================================



def sample_and_plot_rbf_surface(
    rbf_surface,
    tied_points,
    best_point,
    N=500,
    x_range=(0, 1000),
    y_range=(0, 1000),
    threshold=1.73,
    objective_approx=None,
    show_plot=True,
    save_csv=True
):
    if objective_approx is None:
        raise ValueError("You must pass an objective_approx function.")

    # Random x,y
    x_vals = np.random.uniform(x_range[0], x_range[1], N)
    y_vals = np.random.uniform(y_range[0], y_range[1], N)

    # Evaluate RBF surface
    z_vals = rbf_surface(x_vals, y_vals)

    # Filter out points where z < 0
    mask_valid = z_vals >= 0
    x_vals = x_vals[mask_valid]
    y_vals = y_vals[mask_valid]
    z_vals = z_vals[mask_valid]

    # Evaluate objective
    evals = np.array([objective_approx(x_vals[i], y_vals[i], z_vals[i])
                      for i in range(len(x_vals))])

    # Mask for points above threshold
    mask_best = evals >= threshold

    if show_plot:
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection="3d")

        # --- Points below threshold: dark blue ---
        ax.scatter(
            x_vals[~mask_best],
            y_vals[~mask_best],
            z_vals[~mask_best],
            color="#00008B",
            s=40,
            edgecolor="black",
            alpha=0.7
        )

        # --- Points above threshold: Turbo colormap ---
        if mask_best.sum() > 0:
            vmax = evals[mask_best].max()
            norm = plt.Normalize(vmin=threshold, vmax=vmax)
            colors = cm.turbo(norm(evals[mask_best]))

            ax.scatter(
                x_vals[mask_best],
                y_vals[mask_best],
                z_vals[mask_best],
                color=colors,
                s=60,
                edgecolor="black",
                alpha=0.9
            )

        # --- Plot best + tied points in fuchsia ---
        ax.scatter(
            best_point["x"], best_point["y"], best_point["z"],
            color="#FF00FF", s=120, edgecolor="black", label="Best point"
        )

        ax.scatter(
            tied_points["x"], tied_points["y"], tied_points["z"],
            color="#FF00FF", s=80, edgecolor="black", label="Tied points"
        )

        # --- Plot the RBF surface grid ---
        xx, yy = np.meshgrid(
            np.linspace(x_range[0], x_range[1], 40),
            np.linspace(y_range[0], y_range[1], 40)
        )
        zz = rbf_surface(xx, yy)
        zz_plot = np.where(zz >= 0, zz, np.nan)

        ax.plot_surface(xx, yy, zz_plot, alpha=0.3, color="gray")

        ax.set_xlabel("Mismatch")
        ax.set_ylabel("Distance")
        ax.set_zlabel("Equity")
        ax.set_title("Random Points on RBF Surface (Turbo grading)")

        plt.show()

    # --- Save CSV files ---
    if save_csv:
        # Save RBF parameters
        params = {
            "centers_x": rbf_model.xi[0].tolist(),
            "centers_y": rbf_model.xi[1].tolist(),
            "weights": rbf_model.nodes.tolist(),
            "kernel": rbf_model.function,
            "epsilon": rbf_model.epsilon

        }

        with open("rbf_surface_parameters.json", "w") as f:
            json.dump(params, f, indent=4)

        # Save high-value points
        high_value_df = pd.DataFrame({
            "x": x_vals[mask_best],
            "y": y_vals[mask_best],
            "z": z_vals[mask_best],
            "eval": evals[mask_best]
        })

        high_value_df.to_csv("rbf_high_value_points.csv", index=False)

    return {
        "x": x_vals,
        "y": y_vals,
        "z": z_vals,
        "evals": evals,
        "mask_best": mask_best
    }

