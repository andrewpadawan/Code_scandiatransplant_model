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


# Example usage
if __name__ == "__main__":
    summary = summarize_organ_flows(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\csv_logs\matching_20251105_113859.csv")
    

    print(summary)

    # Optional: export to CSV
    
