
from patient_generators.generating_utils import build_serologic_to_genetic
from scipy.stats import truncnorm
import matplotlib.pyplot as plt
import numpy as np

def plot_trunc_normal_HS():
    # Target quartiles and bounds
    q1, median, q3 = 86, 96.5, 100
    lower, upper = 80, 100

    # Fit parameters
    loc, scale = fit_truncnorm(q1, median, q3, lower, upper)
    a, b = (lower - loc) / scale, (upper - loc) / scale
    dist = truncnorm(a, b, loc=loc, scale=scale)

    # Plot PDF
    x = np.linspace(lower, upper, 500)
    pdf = dist.pdf(x)

    # Compute quartiles from the fitted distribution
    q1_val = dist.ppf(0.25)
    median_val = dist.ppf(0.5)
    q3_val = dist.ppf(0.75)

    plt.figure(figsize=(8,5))
    plt.plot(x, pdf, label=f'TruncNorm(loc={loc:.2f}, scale={scale:.2f})')
    plt.axvline(q1_val, color='red', linestyle='--', label=f'Q1={q1_val:.2f}')
    plt.axvline(median_val, color='green', linestyle='--', label=f'Median={median_val:.2f}')
    plt.axvline(q3_val, color='blue', linestyle='--', label=f'Q3={q3_val:.2f}')
    plt.title("Fitted Truncated Normal Distribution for NH cPRA")
    plt.xlabel("cPRA value")
    plt.ylabel("Density")
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_trunc_normal_NH():
    # Target quartiles and bounds
    q1, median, q3 = 0, 3, 8
    lower, upper = 0, 80

    # Fit parameters
    loc, scale = fit_truncnorm(q1, median, q3, lower, upper)
    a, b = (lower - loc) / scale, (upper - loc) / scale
    dist = truncnorm(a, b, loc=loc, scale=scale)

    # Plot PDF
    x = np.linspace(lower, upper, 500)
    pdf = dist.pdf(x)

    # Compute quartiles from the fitted distribution
    q1_val = dist.ppf(0.25)
    median_val = dist.ppf(0.5)
    q3_val = dist.ppf(0.75)

    plt.figure(figsize=(8,5))
    plt.plot(x, pdf, label=f'TruncNorm(loc={loc:.2f}, scale={scale:.2f})')
    plt.axvline(q1_val, color='red', linestyle='--', label=f'Q1={q1_val:.2f}')
    plt.axvline(median_val, color='green', linestyle='--', label=f'Median={median_val:.2f}')
    plt.axvline(q3_val, color='blue', linestyle='--', label=f'Q3={q3_val:.2f}')
    plt.title("Fitted Truncated Normal Distribution for NH cPRA")
    plt.xlabel("cPRA value")
    plt.ylabel("Density")
    plt.legend()
    plt.grid(True)
    plt.show()