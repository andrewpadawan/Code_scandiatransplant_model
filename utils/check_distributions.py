import pandas as pd
import matplotlib.pyplot as plt
import ast
import numpy as np
from scipy.stats import beta
from scipy.optimize import minimize
from patient_generators.generating_utils import build_serologic_to_genetic
from scipy.stats import truncnorm




def check_age_distribution_by_groups(csv_path):
    # Load CSV
    df = pd.read_csv(csv_path)

    # Ensure AGE column exists
    if "AGE" not in df.columns:
        raise ValueError("CSV file does not contain an 'AGE' column")

    # Define age groups
    bins = [0, 19, 44, 64, 74, 90]
    labels = ["0-19", "20-44", "45-64", "65-74", "75-90"]

    # Categorize ages into groups
    df["AGE_GROUP"] = pd.cut(df["AGE"], bins=bins, labels=labels, right=True)

    # Count distribution
    distribution = df["AGE_GROUP"].value_counts().sort_index()

    print("Age distribution by groups:")
    print(distribution)

    # Optional: percentage distribution
    print("\nPercentage distribution:")
    print((distribution / distribution.sum() * 100).round(2))

# Example usage:



def check_age_distribution_by_groups_donors(csv_path):
    # Load CSV
    df = pd.read_csv(csv_path)

    # Ensure AGE column exists
    if "AGE" not in df.columns:
        raise ValueError("CSV file does not contain an 'AGE' column")

    # Define age groups
    
    bins = [16, 55, 65, 90]
    labels = ["16-55", "56-64", "65-90"]

    # Categorize ages into groups
    df["AGE_GROUP"] = pd.cut(df["AGE"], bins=bins, labels=labels, right=True)

    # Count distribution
    distribution = df["AGE_GROUP"].value_counts().sort_index()

    print("Age distribution by groups:")
    print(distribution)

    # Optional: percentage distribution
    print("\nPercentage distribution:")
    print((distribution / distribution.sum() * 100).round(2))

import pandas as pd
from collections import Counter

def check_hla_distributions(csv_path):
    df = pd.read_csv(csv_path)

    # Identify genomic and serologic HLA columns
    genomic_cols   = [col for col in df.columns if col.startswith("Genomic_HLA")]
    serologic_cols = [col for col in df.columns if col.startswith("Serologic_HLA")]

    results = {}

    # Process genomic columns
    for col in genomic_cols:
        locus = col.replace("Genomic_HLA-", "")
        alleles = []
        for entry in df[col].dropna():
            if isinstance(entry, str) and entry.strip().startswith("["):
                try:
                    parsed = ast.literal_eval(entry)
                    alleles.extend(parsed)
                except (ValueError, SyntaxError):
                    alleles.extend(entry.replace(" ", "").split("/"))
            elif isinstance(entry, str):
                alleles.extend(entry.replace(" ", "").split("/"))
            elif isinstance(entry, list):
                alleles.extend(entry)

        counts = Counter(alleles)
        total = sum(counts.values())
        freqs = {allele: round(count/total, 4) for allele, count in counts.items()}

        if locus not in results:
            results[locus] = {}
        results[locus]["genomic"] = {"counts": dict(counts),
                                     "frequencies": freqs,
                                     "total": total}

        print(f"\nGenomic distribution for {locus}:")
        print("Counts:", dict(counts))
        print("Frequencies:", freqs)

    # Process serologic columns
    for col in serologic_cols:
        locus = col.replace("Serologic_HLA-", "")
        antigens = []
        for entry in df[col].dropna():
            if isinstance(entry, str) and entry.strip().startswith("["):
                try:
                    parsed = ast.literal_eval(entry)
                    antigens.extend(parsed)
                except (ValueError, SyntaxError):
                    antigens.extend(entry.replace(" ", "").split("/"))
            elif isinstance(entry, str):
                antigens.extend(entry.replace(" ", "").split("/"))
            elif isinstance(entry, list):
                antigens.extend(entry)

        counts = Counter(antigens)
        total = sum(counts.values())
        freqs = {antigen: round(count/total, 4) for antigen, count in counts.items()}

        if locus not in results:
            results[locus] = {}
        results[locus]["serologic"] = {"counts": dict(counts),
                                       "frequencies": freqs,
                                       "total": total}

        print(f"\nSerologic distribution for {locus}:")
        print("Counts:", dict(counts))
        print("Frequencies:", freqs)

    return results


def hs_distribution(csv_path):
    """
    Reads a CSV of recipients and calculates the distribution of True/False
    in the hs_status column.
    
    Parameters:
        csv_path (str): Path to the CSV file
    
    Returns:
        dict: Counts and proportions of True/False values
    """
    # Load CSV
    df = pd.read_csv(csv_path)
    
    # Ensure hs_status column exists
    if "HS_status" not in df.columns:
        raise ValueError("CSV must contain an 'hs_status' column")
    
    # Count values
    counts = df["HS_status"].value_counts(dropna=False)
    proportions = df["HS_status"].value_counts(normalize=True, dropna=False)
    
    # Return both counts and proportions
    return {
        "counts": counts.to_dict(),
        "proportions": proportions.to_dict()
    }

def summarize_cpra_by_status(csv_file):
    """
    Reads a CSV file with columns 'HS_status' (boolean) and 'cPRA' (numeric).
    Returns a DataFrame with median and IQR of cPRA grouped by HS_status.
    """
    # Load CSV
    df = pd.read_csv(csv_file)
    
    # Ensure HS_status is boolean
    df['HS_status'] = df['HS_status'].astype(bool)
    
    # Group by HS_status
    results = []
    for status, group in df.groupby('HS_status'):
        cpra_values = group['cPRA'].dropna()
        mean= np.median(cpra_values) 
        median = np.median(cpra_values)
        q1 = np.percentile(cpra_values, 25)
        q3 = np.percentile(cpra_values, 75)
        iqr = q3 - q1
        
        results.append({
            
            "HS_status": status,
            "Mean": mean * 100 ,
            "median_cPRA": round(median, 3) * 100 ,
            "Q1_cPRA": round(q1, 3) * 100 ,
            "Q3_cPRA":round(q3, 3) * 100 
        })
    print(pd.DataFrame(results))
    return pd.DataFrame(results)


def summarize_by_cPRA(filepath, column="cPRA"):
    """
    Read a CSV file, extract the cPRA column (values between 0 and 1),
    and summarize distribution into clinically relevant intervals:
      - 0
      - 0.01–0.20
      - 0.21–0.79
      - 0.80–0.97
      - 0.98–1.00
    
    Parameters
    ----------
    filepath : str
        Path to the CSV file.
    column : str, default "cPRA"
        Name of the column containing cPRA values (between 0 and 1).
    
    Returns
    -------
    summary : dict
        Dictionary with % of patients in each interval.
    """
    # Read CSV
    df = pd.read_csv(filepath)
    
    # Extract cPRA column
    values = df[column].dropna()
    total = len(values)
    
    summary = {
        "0": (values == 0).sum() / total * 100,
        "0.01–0.20": ((values >= 0.01) & (values <= 0.20)).sum() / total * 100,
        "0.21–0.79": ((values >= 0.21) & (values <= 0.79)).sum() / total * 100,
        "0.80–0.97": ((values >= 0.80) & (values <= 0.97)).sum() / total * 100,
        "0.98–1.00": ((values >= 0.98) & (values <= 1.00)).sum() / total * 100,
    }
    
    return summary



def plot_cPRA_histogram_percent_from_csv(
    csv_path,
    column="cPRA",
    bins=50,
    title="cPRA values generated for 10000 samples"
):
    """
    Read cPRA values (0–1) from a CSV file and plot histogram as % of patients.
    Converts values to percent (0–100).
    """
    # Load CSV
    df = pd.read_csv(csv_path)

    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in {csv_path}")

    # Extract cPRA values and convert to percent
    samples = df[column].dropna().values
    vals_pct = samples * 100.0

    # Histogram as % of patients
    counts, bin_edges, patches = plt.hist(
        vals_pct,
        bins=bins,
        weights=np.ones_like(vals_pct) / len(vals_pct) * 100.0,
        edgecolor="black"
    )

    plt.xlabel("cPRA (%)", fontsize=20)
    plt.ylabel("Percentage of patients", fontsize=20)  
    plt.title(title, fontsize=20)

    # Recolor bins depending on threshold
    for left, right, patch in zip(bin_edges[:-1], bin_edges[1:], patches):
        if right <= 80:
            patch.set_facecolor("skyblue")
        else:
            patch.set_facecolor("orange")

    # Vertical line at 80%
    plt.axvline(80, color="red", linestyle="--", linewidth=2)

    # Add label for highly sensitized region
    ymax = max(counts) * 1.05
    plt.text(82, ymax, "Highly sensitized", color="orange", fontsize=12, va="bottom")

    # Make y-axis tick labels larger
    plt.tick_params(axis="y", labelsize=20)
    plt.tick_params(axis="x", labelsize=20)
    # Horizontal grid lines from y-axis ticks
    plt.grid(axis="y", linestyle="--", linewidth=2, color="black", alpha=0.8)

    plt.tight_layout()
    plt.show()
