import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.lines as mlines
import matplotlib as mpl

class SA3DScatterWithWeights:
    def __init__(self):
        self.points = []   # (mismatch, distance, equity)
        self.weights = []  # (w1, w2, w3)
        self.labels = []   # run labels
        self.evals = []    # evaluation values

    def add_run(self, mismatch, distance, equity, w1, w2, w3, label, eval_value):
        self.points.append((float(mismatch), float(distance), float(equity)))
        self.weights.append((float(w1), float(w2), float(w3)))
        self.labels.append(str(label))
        self.evals.append(float(eval_value))

    def show(self):
        # Convert to arrays
        points = np.array(self.points, dtype=float).reshape(-1, 3)
        weights = np.array(self.weights, dtype=float).reshape(-1, 3)
        evals = np.array(self.evals, dtype=float)

        xs = points[:, 0]
        ys = points[:, 1]
        zs = points[:, 2]

        # ---------------------------------------------------------
        # COLOR LOGIC
        # ---------------------------------------------------------
        norm = mpl.colors.Normalize(vmin=1.74, vmax=evals.max())
        cmap = mpl.colormaps.get_cmap("viridis")
        colors = [cmap(norm(v)) for v in evals]

        # Identify best runs (rounded to 4 decimals)
        best_value = round(evals.max(), 4)
        best_indices = [i for i, v in enumerate(evals) if round(v, 4) == best_value]

        # Override best runs to red
        for i in best_indices:
            colors[i] = (1, 0, 0, 1)

        # ---------------------------------------------------------
        # LABEL OFFSETS (scaled to data range)
        # ---------------------------------------------------------
        x_off = (xs.max() - xs.min()) * 0.02
        y_off = (ys.max() - ys.min()) * 0.02
        z_off = (zs.max() - zs.min()) * 0.02
        # ---------------------------------------------------------
        # FIGURE LAYOUT (2×2)
        # ---------------------------------------------------------
        fig = plt.figure(figsize=(14, 12))

        # ---------------------------------------------------------
        # Top-left: Mismatch vs Distance
        # ---------------------------------------------------------
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.scatter(xs, ys, c=colors, edgecolors='black', s=160)
        ax1.set_xlabel("Mismatch")
        ax1.set_ylabel("Distance")
        ax1.set_title("Mismatch vs Distance")

        # Label best points (offset, black)
        for i in best_indices:
            ax1.text(xs[i] + x_off, ys[i] + y_off,
                    self.labels[i], fontsize=9, color="black")

        # ---------------------------------------------------------
        # Top-right: Equity vs Mismatch
        # ---------------------------------------------------------
        ax2 = fig.add_subplot(2, 2, 2)
        ax2.scatter(xs, zs, c=colors, edgecolors='black', s=160)
        ax2.set_xlabel("Mismatch")
        ax2.set_ylabel("Equity")
        ax2.set_title("Equity vs Mismatch")

        for i in best_indices:
            ax2.text(xs[i] + x_off, zs[i] + z_off,
                    self.labels[i], fontsize=9, color="black")

        # ---------------------------------------------------------
        # Bottom-left: Distance vs Equity
        # ---------------------------------------------------------
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.scatter(ys, zs, c=colors, edgecolors='black', s=160)
        ax3.set_xlabel("Distance")
        ax3.set_ylabel("Equity")
        ax3.set_title("Distance vs Equity")

        for i in best_indices:
            ax3.text(ys[i] + y_off, zs[i] + z_off,
                    self.labels[i], fontsize=9, color="black")

        # ---------------------------------------------------------
        # Bottom-right: 3D plot
        # ---------------------------------------------------------
        ax4 = fig.add_subplot(2, 2, 4, projection='3d')
        ax4.invert_yaxis()

        for i in range(len(points)):
            ax4.scatter(xs[i], ys[i], zs[i],
                        s=220, c=[colors[i]],
                        marker='o', edgecolors='black',
                        linewidths=1.5, alpha=0.9)

            # Offset label upward in z
            ax4.text(xs[i], ys[i], zs[i] + z_off * 3,
                    f"{self.labels[i]}", fontsize=9, color="black")

        ax4.set_xlabel("Mismatch")
        ax4.set_ylabel("Distance")
        ax4.set_zlabel("Equity")
        ax4.set_title("3D Fitness Components")

        # ---------------------------------------------------------
        # COLORBAR
        # ---------------------------------------------------------
        sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=[ax1, ax2, ax3, ax4],
                            pad=0.1, location="left", shrink=0.8)
        cbar.set_label("Evaluation value")

        plt.show()


# ---------------------------------------------------------
# Instantiate plotter
# ---------------------------------------------------------

plotter = SA3DScatterWithWeights()

# Evaluation values in order (Run 1 → Run 21)
eval_values = [
    1.67687037620386,
    1.75446187059316,
    1.75509502690902,
    1.75514208693659,
    1.72174166637360,
    1.75467948965118,
    1.75415324425573,
    1.71171859588019,
    1.72143931068544,
    1.75477954585285,
    1.75359996924416,
    1.75507358673260,
    1.74533799958452,
    1.75436374717761,
    1.75513882212879,
    1.75494049747912,
    1.75511970406575,
    1.75514737917865,
    1.75120805486178,
    1.75309618753157,
    1.75379843019049
]

# ---------------------------------------------------------
# Add your 21 runs (now with eval_value=eval_values[i])
# ---------------------------------------------------------

plotter.add_run(2.009, 281661.45, 0.910057, 50.430, 533.138, 239.824, "Run 1",  eval_values[0])
plotter.add_run(1.879, 342973.97, 0.933853, 435.361, 428.619, 247.026, "Run 2",  eval_values[1])
plotter.add_run(1.905, 333699.57, 0.890829, 770.741, 809.621, 475.194, "Run 3",  eval_values[2])
plotter.add_run(1.875, 343676.08, 0.925071, 331.426, 338.802, 202.158, "Run 4",  eval_values[3])
plotter.add_run(1.932, 309284.97, 0.86438, 153.410, 431.970, 263.481, "Run 5",  eval_values[4])
plotter.add_run(1.875, 363907.11, 0.916808, 699.074, 576.103, 420.025, "Run 6",  eval_values[5])
plotter.add_run(1.897, 353908.64, 0.920707, 293.836, 235.798, 186.503, "Run 7",  eval_values[6])
plotter.add_run(1.866, 291938.31, 0.916962, 331.663, 506.783, 86.151,  "Run 8",  eval_values[7])
plotter.add_run(1.815, 392269.99, 0.851159, 720.673, 282.693, 210.898, "Run 9",  eval_values[8])
plotter.add_run(1.885, 342950.36, 0.891331, 729.37, 792.14, 475.246,   "Run 10", eval_values[9])
plotter.add_run(1.887, 351491.95, 0.902916, 298.932, 213.345, 175.783, "Run 11", eval_values[10])
plotter.add_run(1.883, 353694.83, 0.917867, 977.77, 878.8, 620.5,      "Run 12", eval_values[11])
plotter.add_run(1.846, 414504.03, 0.936561, 167.2, 5.8, 118.5,         "Run 13", eval_values[12])
plotter.add_run(1.876, 348499.73, 0.886334, 515.44, 462.47, 342.76,    "Run 14", eval_values[13])
plotter.add_run(1.91,  338152.3,  0.913426, 897.92, 868.86, 556.60,    "Run 15", eval_values[14])
plotter.add_run(1.854, 346729.54, 0.906917, 266.04, 222.06, 154.50,    "Run 16", eval_values[15])
plotter.add_run(1.859, 343097.64, 0.785613, 517.25, 497.19, 311.12,    "Run 17", eval_values[16])
plotter.add_run(1.841, 334628.97, 0.868107, 557.61, 541.58, 337.09,    "Run 18", eval_values[17])
plotter.add_run(1.851, 317253.45, 0.870647, 279.69, 385.34, 143.51,    "Run 19", eval_values[18])
plotter.add_run(1.845, 361994.7,  0.891561, 240.84, 152.08, 144.89,    "Run 20", eval_values[19])
plotter.add_run(1.848, 322689.89, 0.860235, 220.05, 296.9, 145.78,     "Run 21", eval_values[20])

# ---------------------------------------------------------
# Show plot
# ---------------------------------------------------------
plotter.show()
































