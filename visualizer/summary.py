import pandas as pd
import re
import os

def normalize_organ(name):
    name = str(name).strip().lower()
    if name in ['kd', 'kidney']:
        return 'Kidney'
    elif name in ['lv', 'liver']:
        return 'Liver'
    elif name in ['ht', 'heart']:
        return 'Heart'
    return name.capitalize()

def summarize_organ_flows(csv_path, output_dir="logs/summary_logs"):
    if not csv_path or not os.path.exists(csv_path):
        if csv_path is None:
            print("No match file was provided, skipping summary.")
        else: print(f"Match file not found: {csv_path}") 
        return { "summary_table": None, "city_flow_table": None, "summary_path": None, "flow_path": None }
    df = pd.read_csv(csv_path)
    df["ORGAN_TYPE"] = df["RECIPIENT_ORGAN"].apply(normalize_organ)

    # Count donations and receptions per city
    donor_counts = (
        df.groupby(["DONOR_CITY", "ORGAN_TYPE"])
          .size()
          .reset_index(name="NUM_DONATED")
          .rename(columns={"DONOR_CITY": "CITY"})
    )

    recipient_counts = (
        df.groupby(["RECIPIENT_CITY", "ORGAN_TYPE"])
          .size()
          .reset_index(name="NUM_RECEIVED")
          .rename(columns={"RECIPIENT_CITY": "CITY"})
    )

    # Merge donation and reception counts
    merged = pd.merge(donor_counts, recipient_counts, on=["CITY", "ORGAN_TYPE"], how="outer")
    merged["NUM_DONATED"] = merged["NUM_DONATED"].fillna(0).astype(int)
    merged["NUM_RECEIVED"] = merged["NUM_RECEIVED"].fillna(0).astype(int)
    merged["NET_FLOW"] = merged["NUM_RECEIVED"] - merged["NUM_DONATED"]

    # Count total transfers between city pairs
    city_pair_counts = (
        df.groupby(["DONOR_CITY", "RECIPIENT_CITY", "ORGAN_TYPE"])
          .size()
          .reset_index(name="NUM_TRANSFERS")
    )

    # Extract timestamp tag from filename
    match = re.search(r"(matching_\d{8}_\d{6})", os.path.basename(csv_path))
    tag = match.group(1) if match else "summary"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save both tables
    summary_path = os.path.join(output_dir, f"summary_{tag}.csv")
    flow_path = os.path.join(output_dir, f"city_flows_{tag}.csv")

    merged.to_csv(summary_path, index=False)
    city_pair_counts.to_csv(flow_path, index=False)

    return {
        "summary_table": merged,
        "city_flow_table": city_pair_counts,
        "summary_path": summary_path,
        "flow_path": flow_path
    }

def summarize_organ_flows_export_import(csv_path, output_dir="logs/summary_logs"):
    """
    Summarizes international organ flows:
    - Counts organs donated and received per city (only cross-border)
    - Computes net flow (imports - exports)
    - Counts transfers between city pairs (only cross-border)
    """

    # -----------------------------
    # 1. Validate input
    # -----------------------------
    if not csv_path or not os.path.exists(csv_path):
        if csv_path is None:
            print("No match file was provided, skipping summary.")
        else:
            print(f"Match file not found: {csv_path}")
        return {
            "summary_table": None,
            "city_flow_table": None,
            "summary_path": None,
            "flow_path": None
        }

    # -----------------------------
    # 2. Load data
    # -----------------------------
    df = pd.read_csv(csv_path)
    df["ORGAN_TYPE"] = df["RECIPIENT_ORGAN"].apply(normalize_organ)

    # -----------------------------
    # 3. City → Country mapping
    # -----------------------------
    CITY_TO_COUNTRY = {

        "Aarhus": "Denmark",
        "Copenhagen": "Denmark",
        "Odense": "Denmark",
        "Skane": "Sweden",
        "Gothenburg": "Sweden",
        "Stockholm": "Sweden",
        "Uppsala": "Sweden",
        "Oslo": "Norway",
        "Reykjavik": "Iceland",
        "Helsinki": "Finland",
        "Tartu": "Estonia"
    }

    df["DONOR_COUNTRY"] = df["DONOR_CITY"].map(CITY_TO_COUNTRY)
    df["RECIPIENT_COUNTRY"] = df["RECIPIENT_CITY"].map(CITY_TO_COUNTRY)

    # Warn if any cities are missing
    missing_cities = df[df["DONOR_COUNTRY"].isna() | df["RECIPIENT_COUNTRY"].isna()]
    if not missing_cities.empty:
        print("Warning: Some cities have no country mapping:")
        print(missing_cities[["DONOR_CITY", "RECIPIENT_CITY"]].drop_duplicates())

    # -----------------------------
    # 4. Keep only international flows
    # -----------------------------
    df = df[df["DONOR_COUNTRY"] != df["RECIPIENT_COUNTRY"]]

    # -----------------------------
    # 5. Count donations and receptions per city
    # -----------------------------
    donor_counts = (
        df.groupby(["DONOR_CITY", "ORGAN_TYPE"])
          .size()
          .reset_index(name="NUM_DONATED")
          .rename(columns={"DONOR_CITY": "CITY"})
    )

    recipient_counts = (
        df.groupby(["RECIPIENT_CITY", "ORGAN_TYPE"])
          .size()
          .reset_index(name="NUM_RECEIVED")
          .rename(columns={"RECIPIENT_CITY": "CITY"})
    )

    # Merge donation and reception counts
    merged = pd.merge(
        donor_counts,
        recipient_counts,
        on=["CITY", "ORGAN_TYPE"],
        how="outer"
    )

    merged["NUM_DONATED"] = merged["NUM_DONATED"].fillna(0).astype(int)
    merged["NUM_RECEIVED"] = merged["NUM_RECEIVED"].fillna(0).astype(int)
    merged["NET_FLOW"] = merged["NUM_RECEIVED"] - merged["NUM_DONATED"]

    # -----------------------------
    # 6. Count international transfers between city pairs
    # -----------------------------
    city_pair_counts = (
        df.groupby(["DONOR_CITY", "RECIPIENT_CITY", "ORGAN_TYPE"])
          .size()
          .reset_index(name="NUM_TRANSFERS")
    )

    # -----------------------------
    # 7. Extract timestamp tag from filename
    # -----------------------------
    match = re.search(r"(matching_\d{8}_\d{6})", os.path.basename(csv_path))
    tag = match.group(1) if match else "summary"

    # -----------------------------
    # 8. Save outputs
    # -----------------------------
    os.makedirs(output_dir, exist_ok=True)

    summary_path = os.path.join(output_dir, f"summary_{tag}.csv")
    flow_path = os.path.join(output_dir, f"city_flows_{tag}.csv")

    merged.to_csv(summary_path, index=False)
    city_pair_counts.to_csv(flow_path, index=False)

    # -----------------------------
    # 9. Return results
    # -----------------------------
    return {
        "summary_table": merged,
        "city_flow_table": city_pair_counts,
        "summary_path": summary_path,
        "flow_path": flow_path
    }

def summarize_organ_flows_countries(csv_path, output_dir="logs/summary_logs"):
    """
    Summarizes international organ flows at the COUNTRY level:
    - NUM_EXPORTED: organs sent abroad
    - NUM_IMPORTED: organs received from abroad
    - NET_FLOW: imports - exports
    - city-to-city international transfers (optional)
    """

    # -----------------------------
    # 1. Validate input
    # -----------------------------
    if not csv_path or not os.path.exists(csv_path):
        if csv_path is None:
            print("No match file was provided, skipping summary.")
        else:
            print(f"Match file not found: {csv_path}")
        return {
            "summary_table": None,
            "city_flow_table": None,
            "summary_path": None,
            "flow_path": None
        }

    # -----------------------------
    # 2. Load data
    # -----------------------------
    df = pd.read_csv(csv_path)
    df["ORGAN_TYPE"] = df["RECIPIENT_ORGAN"].apply(normalize_organ)

    # -----------------------------
    # 3. City → Country mapping
    # -----------------------------
    CITY_TO_COUNTRY = {
        "Aarhus": "Denmark",
        "Copenhagen": "Denmark",
        "Odense": "Denmark",
        "Skane": "Sweden",
        "Gothenburg": "Sweden",
        "Stockholm": "Sweden",
        "Uppsala": "Sweden",
        "Oslo": "Norway",
        "Reykjavik": "Iceland",
        "Helsinki": "Finland",
        "Tartu": "Estonia"
    }

    df["DONOR_COUNTRY"] = df["DONOR_CITY"].map(CITY_TO_COUNTRY)
    df["RECIPIENT_COUNTRY"] = df["RECIPIENT_CITY"].map(CITY_TO_COUNTRY)

    df_all = df.copy()

    missing = df[df["DONOR_COUNTRY"].isna() | df["RECIPIENT_COUNTRY"].isna()]
    if not missing.empty:
        print("Warning: Some cities have no country mapping:")
        print(missing[["DONOR_CITY", "RECIPIENT_CITY"]].drop_duplicates())

    # -----------------------------
    # 4. Keep only international flows
    # -----------------------------
    df = df[df["DONOR_COUNTRY"] != df["RECIPIENT_COUNTRY"]]

    # -----------------------------
    # 5. Compute exports and imports per COUNTRY
    # -----------------------------
    exports = (
        df.groupby(["DONOR_COUNTRY", "ORGAN_TYPE"])
          .size()
          .reset_index(name="NUM_EXPORTED")
          .rename(columns={"DONOR_COUNTRY": "COUNTRY"})
    )

    imports = (
        df.groupby(["RECIPIENT_COUNTRY", "ORGAN_TYPE"])
          .size()
          .reset_index(name="NUM_IMPORTED")
          .rename(columns={"RECIPIENT_COUNTRY": "COUNTRY"})
    )

    # -----------------------------
    # 6. Merge into a single country-level summary
    # -----------------------------
    summary = pd.merge(exports, imports, on=["COUNTRY", "ORGAN_TYPE"], how="outer")

    summary["NUM_IMPORTED"] = summary["NUM_IMPORTED"].fillna(0).astype(int)
    summary["NUM_EXPORTED"] = summary["NUM_EXPORTED"].fillna(0).astype(int)

    summary["NET_FLOW"] = summary["NUM_IMPORTED"] - summary["NUM_EXPORTED"]

    # -----------------------------
    # X. Total kidneys transplanted IN each country
    # -----------------------------
    kidney_counts = (
        df_all[df_all["ORGAN_TYPE"] == "Kidney"]
        .groupby("RECIPIENT_COUNTRY")
        .size()
        .reset_index(name="TOTAL_KIDNEYS_TRANSPLANTED")
        .rename(columns={"RECIPIENT_COUNTRY": "COUNTRY"})
    )

    summary = pd.merge(summary, kidney_counts, on="COUNTRY", how="left")
    summary["TOTAL_KIDNEYS_TRANSPLANTED"] = summary["TOTAL_KIDNEYS_TRANSPLANTED"].fillna(0).astype(int)
    # -----------------------------
    # Reorder columns: imported before exported
    # -----------------------------
    desired_col_order = [
        "COUNTRY",
        "ORGAN_TYPE",
        "NUM_IMPORTED",
        "NUM_EXPORTED",
        "NET_FLOW",
        "TOTAL_KIDNEYS_TRANSPLANTED"
    ]

# Keep only columns that exist (robust to missing fields)
    summary = summary[[col for col in desired_col_order if col in summary.columns]]

    # -----------------------------
    # 7. Apply custom country ordering
    # -----------------------------
    desired_order = [
        "Denmark",
        "Norway",
        "Finland",
        "Sweden",
        "Estonia",
        "Iceland"
    ]

    summary["COUNTRY"] = pd.Categorical(
        summary["COUNTRY"],
        categories=desired_order,
        ordered=True
    )

    summary = summary.sort_values("COUNTRY")

    # -----------------------------
    # 8. City-to-city international flows
    # -----------------------------
    city_pair_counts = (
        df.groupby(["DONOR_CITY", "RECIPIENT_CITY", "ORGAN_TYPE"])
          .size()
          .reset_index(name="NUM_TRANSFERS")
    )

    # -----------------------------
    # 9. Extract timestamp tag
    # -----------------------------
    match = re.search(r"(matching_\d{8}_\d{6})", os.path.basename(csv_path))
    tag = match.group(1) if match else "summary"

    # -----------------------------
    # 10. Save outputs
    # -----------------------------
    os.makedirs(output_dir, exist_ok=True)

    summary_path = os.path.join(output_dir, f"summary_{tag}.csv")
    flow_path = os.path.join(output_dir, f"city_flows_{tag}.csv")

    summary.to_csv(summary_path, index=False)
    city_pair_counts.to_csv(flow_path, index=False)

    # -----------------------------
    # 11. Return results
    # -----------------------------
    return {
        "summary_table": summary,
        "city_flow_table": city_pair_counts,
        "summary_path": summary_path,
        "flow_path": flow_path
    }


# Example usage
if __name__ == "__main__":
    summary = summarize_organ_flows(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\csv_logs\matching_20251105_113859.csv")
    

    print(summary)

    # Optional: export to CSV
    
