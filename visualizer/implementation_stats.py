import pandas as pd
import re
import os
from math import radians, sin, cos, sqrt, atan2
from book_keeping.locations import *
from matching.match_utils import count_mismatches
# Calculate total number of mismatches
# Calculate distance travelled
# Calculate equity coefficient


import os
import re
import pandas as pd

import os
import re
import pandas as pd

def calculate_implementation_stats(csv_path, output_dir="logs/stats"):
    # Load the main matching file
    df = pd.read_csv(csv_path)

    # Extract the tag (matching_YYYYMMDD_HHMMSS)
    match = re.search(r"(matching_\d{8}_\d{6})", os.path.basename(csv_path))
    tag = match.group(1) if match else "stats"

    # Build the path to the summary file
    summary_path = os.path.join("logs/summary_logs", f"summary_{tag}.csv")
    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"Expected summary file not found: {summary_path}")

    # Load the summary file
    summary_df = pd.read_csv(summary_path)

    # Compute stats (expects calculate_mismatches to return six values)
    average_distance_travelled_incl_local, total_distance_travelled_incl_local = calculate_distance_travelled_incl_local(df)
    average_distance_travelled, total_distance_travelled = calculate_distance_travelled(df)

    (
        average_mismatches, total_mismatches,
        average_ab_mismatches, total_ab_mismatches,
        average_drb1_mismatches, total_drb1_mismatches, total_mismatch_distribution,
        ab_mismatch_distribution,
        drb1_mismatch_distribution
    ) = calculate_mismatches(df)

    equity_coefficient_df, average_equity_coefficient = calculate_equity_coefficent(summary_df)

    desired_order = [
    "COUNTRY",
    "ORGAN_TYPE",
    "NUM_IMPORTED",
    "NUM_EXPORTED",
    "NET_FLOW",
    "TOTAL_KIDNEYS_TRANSPLANTED",
    "equity_coeff"
    ]

# Reorder only if all columns exist
    existing_cols = [c for c in desired_order if c in equity_coefficient_df.columns]
    equity_coefficient_df = equity_coefficient_df[existing_cols]


    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save equity coefficient DataFrame separately for legibility
    equity_path = os.path.join(output_dir, f"equity_coefficients_{tag}.csv")
    equity_coefficient_df.to_csv(equity_path, index=False)

    # Build a machine-friendly stats DataFrame (numeric values)
    stats_record = {
        "average_distance_travelled_incl_local_km": average_distance_travelled_incl_local,
        "total_distance_travelled_incl_local_km": total_distance_travelled_incl_local,
        "average_distance_travelled_km": average_distance_travelled,
        "total_distance_travelled_km": total_distance_travelled,
        "average_mismatches_overall": average_mismatches,
        "total_mismatches_overall": total_mismatches,
        "average_mismatches_AplusB": average_ab_mismatches,
        "total_mismatches_AplusB": total_ab_mismatches,
        "average_mismatches_DRB1": average_drb1_mismatches,
        "total_mismatches_DRB1": total_drb1_mismatches,
        "average_equity_coefficient": average_equity_coefficient,
        "equity_coefficients_csv": equity_path,
        "total_mismatch_distribution": total_mismatch_distribution,
        "ab_mismatch_distribution" : ab_mismatch_distribution,
        "drb1_mismatch_distribution": drb1_mismatch_distribution
    }
    stats_df = pd.DataFrame([stats_record])

    # Save numeric stats CSV
    stats_path = os.path.join(output_dir, f"stats_{tag}.csv")
    stats_df.to_csv(stats_path, index=False)

    # --- Nicely formatted console output for humans ---
    def fmt_num(x, places=2):
        if x is None:
            return "N/A"
        try:
            if isinstance(x, int):
                return f"{x:,d}"
            return f"{x:,.{places}f}"
        except Exception:
            return str(x)

    print("\n=== Implementation Summary ===\n")
    print(f"Tag: {tag}\n")

    print("Distance (including local):")
    print(f"  Average: {fmt_num(average_distance_travelled_incl_local)} km")
    print(f"  Total:   {fmt_num(total_distance_travelled_incl_local)} km\n")

    print("Distance (excluding local):")
    print(f"  Average: {fmt_num(average_distance_travelled)} km")
    print(f"  Total:   {fmt_num(total_distance_travelled)} km\n")

    print("Mismatches overall:")
    print(f"  Average mismatches per case: {fmt_num(average_mismatches, 3)}")
    print(f"  Total mismatches:            {fmt_num(total_mismatches, 0)}\n")

    print("Mismatches A + B:")
    print(f"  Average mismatches per case: {fmt_num(average_ab_mismatches, 3)}")
    print(f"  Total mismatches:            {fmt_num(total_ab_mismatches, 0)}\n")

    print("Mismatches DRB1:")
    print(f"  Average mismatches per case: {fmt_num(average_drb1_mismatches, 3)}")
    print(f"  Total mismatches:            {fmt_num(total_drb1_mismatches, 0)}\n")

    print("Equity coefficients:")
    print(f"  Average equity coefficient: {fmt_num(average_equity_coefficient, 6)}")
    print(f"  Full equity table saved to: {equity_path}\n")

    print("Total mismatch distribution: ")
    print(total_mismatch_distribution)

    print("AB mismatch distribution: ")
    print(ab_mismatch_distribution)

    print("DRB1 mismatch distribution: ")
    print(drb1_mismatch_distribution)


    # Print a readable slice of the equity table
    if not equity_coefficient_df.empty:
        # Round numeric columns for display only
        display_df = equity_coefficient_df.copy()
        for col in display_df.select_dtypes(include=["float", "float64", "int"]).columns:
            display_df[col] = display_df[col].round(6)
        print("Equity coefficient table (top rows):")
        print(display_df.head(10).to_string(index=False))
    else:
        print("Equity coefficient table is empty.\n")

    print("\nSaved numeric stats CSV to:", stats_path)
    print("Saved equity CSV to:         ", equity_path)
    print("\n=== End Summary ===\n")

    # Return both paths for downstream use
    return stats_path, equity_path




def calculate_distance_travelled_incl_local(df):
    distances = []

    for _, row in df.iterrows():
        donor_city = row["DONOR_CITY"]
        recipient_city = row["RECIPIENT_CITY"]

        # Skip if either city is missing from your lookup
        if donor_city not in CITY_COORDS_LONG_LAT or recipient_city not in CITY_COORDS_LONG_LAT:
            continue

        lat1, lon1 = CITY_COORDS_LONG_LAT[donor_city]
        lat2, lon2 = CITY_COORDS_LONG_LAT[recipient_city]

        distance = haversine_distance(lat1, lon1, lat2, lon2)
        distances.append(distance)

    if not distances:
        return 0, 0

    average_distance = sum(distances) / len(distances)
    total_distance = sum(distances)

    return average_distance, total_distance


def calculate_distance_travelled(df):
    allowed_groups = {
        "AllocationPriority.PRIORITY_1", "AllocationPriority.PRIORITY_2", "AllocationPriority.PRIORITY_3",
        "AllocationPriority.PRIORITY_4", "AllocationPriority.PRIORITY_5", "AllocationPriority.PRIORITY_7","AllocationPriority.PAYBACK", "AllocationPriority.SURPLUS"
    }

    distances = []

    for _, row in df.iterrows():
        # Filter by allowed priority groups
        if row.get("PRIORITY_GROUP") not in allowed_groups:
            continue

        donor_city = row["DONOR_CITY"]
        recipient_city = row["RECIPIENT_CITY"]

        # Skip if either city is missing from your lookup
        if donor_city not in CITY_COORDS_LONG_LAT or recipient_city not in CITY_COORDS_LONG_LAT:
            raise 
            

        lat1, lon1 = CITY_COORDS_LONG_LAT[donor_city]
        lat2, lon2 = CITY_COORDS_LONG_LAT[recipient_city]

        distance = haversine_distance(lat1, lon1, lat2, lon2)
        distances.append(distance)

    if not distances:
        return 0, 0

    average_distance = sum(distances) / len(distances)
    total_distance = sum(distances)

    return average_distance, total_distance


def calculate_equity_coefficent(df):


    # Optional: ensure numeric columns are parsed correctly
    numeric_cols = [
        "NUM_EXPORTED",
        "NUM_IMPORTED",
        "NET_FLOW",
        "TOTAL_KIDNEYS_TRANSPLANTED"
    ]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    df["equity_coeff"] = 1 - ( (df["NUM_IMPORTED"] - df["NUM_EXPORTED"]).abs() / df["TOTAL_KIDNEYS_TRANSPLANTED"] )

    average_equity_coeff = df["equity_coeff"].mean()
    return df, average_equity_coeff


def calculate_mismatches(df):
    """
    Returns:
      average_mismatches, total_mismatches,
      average_ab_mismatches, total_ab_mismatches,
      average_drb1_mismatches, total_drb1_mismatches,
      mismatch_distribution (dict: mismatch_count → frequency)
    """

    overall_values = []
    ab_values = []
    drb1_values = []

    for _, row in df.iterrows():
        # Extract donor/recipient allele lists (already parsed before this function)
        donor_a = row.get("DONOR_Serologic_HLA-A")
        donor_b = row.get("DONOR_Serologic_HLA-B")
        donor_drb1 = row.get("DONOR_Serologic_HLA-DRB1") 

        rec_a = row.get("RECIPIENT_Serologic_HLA-A") 
        rec_b = row.get("RECIPIENT_Serologic_HLA-B") 
        rec_drb1 = row.get("RECIPIENT_Serologic_HLA-DRB1")

        # Compute mismatches
        mism_a = count_mismatches(donor_a, rec_a)
        mism_b = count_mismatches(donor_b, rec_b)
        mism_drb1 = count_mismatches(donor_drb1, rec_drb1)

        # Aggregate
        total_row_mismatch = mism_a + mism_b + mism_drb1
        ab_row_mismatch = mism_a + mism_b
        drb1_row_mismatch = mism_drb1

        overall_values.append(total_row_mismatch)
        ab_values.append(ab_row_mismatch)
        drb1_values.append(drb1_row_mismatch)

    # Helper to compute average + total
    def stats(values):
        if not values:
            return 0, 0
        total = sum(values)
        avg = total / len(values)
        return avg, total

    average_mismatches, total_mismatches = stats(overall_values)
    average_ab_mismatches, total_ab_mismatches = stats(ab_values)
    average_drb1_mismatches, total_drb1_mismatches = stats(drb1_values)

    # ---------------------------------------------------------
    # NEW: mismatch distribution based on actual data
    # ---------------------------------------------------------
    total_mismatch_distribution = (
        pd.Series(overall_values)
        .value_counts()
        .sort_index()
        .to_dict()
    )
    ab_mismatch_distribution = (
        pd.Series(ab_values)
        .value_counts()
        .sort_index()
        .to_dict()
    )
    drb1_mismatch_distribution = (
        pd.Series(drb1_values)
        .value_counts()
        .sort_index()
        .to_dict()
    )

    return (
        average_mismatches, total_mismatches,
        average_ab_mismatches, total_ab_mismatches,
        average_drb1_mismatches, total_drb1_mismatches,
        total_mismatch_distribution,
        ab_mismatch_distribution,
        drb1_mismatch_distribution
    )




#]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c
