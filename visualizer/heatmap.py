import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_transfer_heatmap(file_path, organ_type="Kidney"):
    df = pd.read_csv(file_path)
    df = df[df["ORGAN_TYPE"] == organ_type]

    pivot = df.pivot_table(
        index="DONOR_CITY",
        columns="RECIPIENT_CITY",
        values="NUM_TRANSFERS",
        aggfunc="sum",
        fill_value=0
    )

    plt.figure(figsize=(12, 8))
    ax = sns.heatmap(
        pivot,
        annot=True,
        fmt="d",
        cmap="viridis",
        cbar=True
    )

    # Move x-axis labels to the top
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    # Rotate labels to horizontal
    plt.xticks(rotation=0)

    plt.title(f"Organ Transfers Heatmap ({organ_type})", fontsize=16, pad=30)
    plt.xlabel("Recipient City")
    plt.ylabel("Donor City")
    plt.tight_layout()
    plt.show()
