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

def summarize_organ_flows(csv_path, output_dir="summary_logs"):
    df = pd.read_csv(csv_path)
    df["ORGAN_TYPE"] = df["RECIPIENT_ORGAN"].apply(normalize_organ)

    flow_summary = (
        df.groupby(["DONOR_CITY", "RECIPIENT_CITY", "ORGAN_TYPE"])
          .size()
          .reset_index(name="NUM_TRANSFERS")
          .sort_values("NUM_TRANSFERS", ascending=False)
    )

    flow_matrix = flow_summary.pivot_table(
        index="DONOR_CITY",
        columns="RECIPIENT_CITY",
        values="NUM_TRANSFERS",
        aggfunc="sum",
        fill_value=0
    )

    donor_counts = (
        df.groupby(["DONOR_CITY", "ORGAN_TYPE"])
          .size()
          .reset_index(name="NUM_DONATED")
          .sort_values("NUM_DONATED", ascending=False)
    )

    recipient_counts = (
        df.groupby(["RECIPIENT_CITY", "ORGAN_TYPE"])
          .size()
          .reset_index(name="NUM_RECEIVED")
          .sort_values("NUM_RECEIVED", ascending=False)
    )

    # Extract timestamp tag from filename
    match = re.search(r"(matching_\d{8}_\d{6})", os.path.basename(csv_path))
    tag = match.group(1) if match else "summary"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"summary_{tag}.csv")
    flow_summary.to_csv(output_path, index=False)

    return {
        "flow_summary": flow_summary,
        "flow_matrix": flow_matrix,
        "donor_counts": donor_counts,
        "recipient_counts": recipient_counts,
        "output_path": output_path
    }

# Example usage
if __name__ == "__main__":
    summary = summarize_organ_flows(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\csv_logs\matching_20251031_140724.csv")
    

    # Access individual summaries
    print("\nOrgan Flow Summary:")
    print(summary["flow_summary"].head())

    print("\nDonor Counts:")
    print(summary["donor_counts"].head())

    print("\nRecipient Counts:")
    print(summary["recipient_counts"].head())

    # Optional: export to CSV
    
