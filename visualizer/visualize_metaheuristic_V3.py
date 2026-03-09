import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.lines as mlines


class SA3DScatterWithWeights:
    def __init__(self):
        self.points = []   # (mismatch, distance, equity)
        self.weights = []  # (w1, w2)
        self.labels = []   # run labels
        self.evals = []    # evaluation values

    def add_run(self, mismatch, distance, equity, w1, w2, label, eval_value):
        self.points.append((float(mismatch), float(distance), float(equity)))
        self.weights.append((float(w1), float(w2)))
        self.labels.append(str(label))
        self.evals.append(float(eval_value))

    def show(self):
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        ax.invert_yaxis()

        points = np.array(self.points, dtype=float).reshape(-1, 3)
        weights = np.array(self.weights, dtype=float).reshape(-1, 2)
        evals = np.array(self.evals, dtype=float)

        xs = points[:, 0]
        ys = points[:, 1]
        zs = points[:, 2]

        w1 = weights[:, 0]
        w2 = weights[:, 1]

        # Color mapping
        norm = mpl.colors.Normalize(vmin=1.50, vmax=evals.max())
        cmap = mpl.colormaps.get_cmap("viridis")
        colors = [cmap(norm(v)) for v in evals]

        # Best runs (rounded to 4 decimals)
        best_value = round(evals.max(), 4)
        best_indices = [i for i, v in enumerate(evals) if round(v, 4) == best_value]

        for i in best_indices:
            colors[i] = (1, 0, 0, 1)  # red

        # Label offset
        z_range = zs.max() - zs.min() if len(zs) > 1 else 1
        label_offset = z_range * 0.05

        # Plot points
        for i in range(len(points)):
            ax.scatter(
                xs[i], ys[i], zs[i],
                s=220,
                c=[colors[i]],
                marker='o',
                edgecolors='black',
                linewidths=1.5,
                alpha=0.9
            )

            ax.text(
                xs[i],
                ys[i],
                zs[i] + label_offset,
                f"{self.labels[i]}",
                fontsize=10
            )

        ax.set_xlabel("Mismatch")
        ax.set_ylabel("Distance")
        ax.set_zlabel("Equity")

        # Legend
        legend_handles = []
        for i in range(len(points)):
            handle = mlines.Line2D(
                [], [], color=colors[i], marker='o', linestyle='None',
                markersize=10,
                label=f"{self.labels[i]}  (w1={int(w1[i])}, w2={int(w2[i])})"
            )
            legend_handles.append(handle)

        ax.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.05, 1))

        # Colorbar
        sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, pad=0.15, location="left")
        cbar.set_label("Evaluation value")

        plt.tight_layout()
        plt.show()


# -------------------------
# Load Excel sheet SA_V2
# -------------------------
df = pd.read_csv("metaheuristic/result_V3.csv", sep=";")

print(df)

scatter = SA3DScatterWithWeights()

for _, row in df.iterrows():
    scatter.add_run(
        mismatch=row["Average mismatch"],
        distance=row["Distance"],
        equity=row["equity_score"],
        w1=row["mismatch_w"],
        w2=row["distance_w"],
        label=row["Run"],
        eval_value=row["best_eval"]
    )

# Show plot
scatter.show()




























