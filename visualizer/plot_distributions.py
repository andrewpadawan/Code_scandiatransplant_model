import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta
import pandas as pd
import matplotlib.pyplot as plt

def plot_beta_dist_cPRA():
    pi0, piH = 0.62, 0.16
    piL = 1.0 - pi0 - piH  # 0.22

    aL, bL = 1.4892255106168255, 7.838299843126989
    aH, bH = 5.089324508243971, 0.3206297252229449

    xL = np.linspace(0.0, 0.80, 800)
    xH = np.linspace(0.80, 1.00, 400)

    cL0 = beta.cdf(0.0, aL, bL); cL1 = beta.cdf(0.80, aL, bL)
    cH0 = beta.cdf(0.80, aH, bH); cH1 = beta.cdf(1.0, aH, bH)
    denL = max(cL1 - cL0, 1e-12)
    denH = max(cH1 - cH0, 1e-12)

    pdfL_tr = beta.pdf(xL, aL, bL) / denL
    pdfH_tr = beta.pdf(xH, aH, bH) / denH

    pdfL_w = piL * pdfL_tr
    pdfH_w = piH * pdfH_tr

    plt.figure(figsize=(9,5))
    plt.plot(xL, pdfL_w, label=f"Lower Beta(α={aL:.2f}, β={bL:.2f})")
    plt.plot(xH, pdfH_w, label=f"High Beta(α={aH:.2f}, β={bH:.2f})", color="orange")
    plt.axvline(0.80, color="red", linestyle="--", label="80% cutoff")

    # Observed proportions
    p_obs = {
        "0": 0.62,
        "1-20": 0.08,
        "21-79": 0.14,
        "80-97": 0.07,
        "98-100": 0.09
    }

    bins = [(0.00, 0.01, p_obs["0"]),   # treat 0% as spanning [0,0.01]
            (0.01, 0.20, p_obs["1-20"]),
            (0.21, 0.79, p_obs["21-79"]),
            (0.80, 0.97, p_obs["80-97"]),
            (0.98, 1.00, p_obs["98-100"])]


    for lo, hi, p in bins:
        mid = 0.5*(lo+hi)
        width = hi - lo
        height = p / max(width, 1e-12)
        plt.bar(mid, height, width=width, alpha=0.25, color="gray", edgecolor="black")

    plt.xlabel("cPRA proportion")
    plt.ylabel("Density / Bin height")
    plt.title("Mixture-weighted Beta vs. observed bins")
    plt.legend()
    plt.tight_layout()
    plt.show()



def plot_mismatch_histograms(csv_path):
    """
    Reads RECIPIENT_DRB1_mismatches and RECIPIENT_AB_mismatches
    from a CSV file and plots their histograms.
    """
    # Load the CSV
    df = pd.read_csv(csv_path)

    # Extract the two columns
    cols = ["RECIPIENT_DRB1_mismatches", "RECIPIENT_AB_mismatches"]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    # Plot histograms
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.hist(df["RECIPIENT_DRB1_mismatches"].dropna(), bins=20, color="steelblue")
    plt.title("DRB1 Mismatches")
    plt.xlabel("Mismatches")
    plt.ylabel("Frequency")

    plt.subplot(1, 2, 2)
    plt.hist(df["RECIPIENT_AB_mismatches"].dropna(), bins=20, color="darkorange")
    plt.title("AB Mismatches")
    plt.xlabel("Mismatches")
    plt.ylabel("Frequency")

    plt.tight_layout()
    plt.show()


import pandas as pd
import matplotlib.pyplot as plt

import pandas as pd
import matplotlib.pyplot as plt
import ast

import pandas as pd
import matplotlib.pyplot as plt
import ast

def plot_hla_allele_frequencies(csv_path):
    """
    Reads Genomic_HLA-A, Genomic_HLA-B, and Genomic_HLA-DRB1 from a CSV.
    Each cell contains a string like "['A*02', 'A*03']".
    Parses alleles, computes relative frequencies, and plots them with labels.
    """
    df = pd.read_csv(csv_path)

    hla_cols = ["Genomic_HLA-A", "Genomic_HLA-B", "Genomic_HLA-DRB1"]
    missing = [c for c in hla_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    plt.figure(figsize=(18, 12))

    for i, col in enumerate(hla_cols, 1):
        alleles = []

        for entry in df[col].dropna():
            try:
                parsed = ast.literal_eval(entry)
                if isinstance(parsed, list):
                    alleles.extend(parsed)
            except:
                cleaned = entry.strip("[]").replace("'", "")
                alleles.extend([a.strip() for a in cleaned.split(",") if a.strip()])

        freq = pd.Series(alleles).value_counts(normalize=True).sort_values(ascending=False)

        plt.subplot(3, 1, i)
        bars = plt.bar(freq.index, freq.values, color="steelblue")
        plt.title(f"{col} Allele Relative Frequencies")
        plt.ylabel("Relative Frequency")
        plt.xticks(rotation=90)

        # Add frequency labels above each bar
        for bar, value in zip(bars, freq.values):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{value:.3f}",
                ha="center",
                va="bottom",
                fontsize=8
            )

    plt.tight_layout()
    plt.show()
