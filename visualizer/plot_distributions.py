import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta

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
