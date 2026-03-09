import pandas as pd
import glob
import os
from utils.scenario_loader import load_organs
from matching.priority_grouping import check_priority_7
#from matching.priority_ordering import ordering_priority_7_metaheuristic
import pandas as pd
import ast
from metaheuristic.aux_meta import *
from metaheuristic.ordering import *
# Folder containing your CSV files
import numpy as np


folder_path = r"C:\Users\reddr\Documents\Scandiatransplant_modelling\metaheuristic\files"

# Load all CSVs except advanced_donor.csv
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
csv_files = [f for f in csv_files if not f.endswith("advanced_donor.csv")]

recipient_df_list = [pd.read_csv(file) for file in csv_files]

# Load the special file separately
advanced_donor_path = os.path.join(folder_path, "advanced_donor.csv")
advanced_donor_df = pd.read_csv(advanced_donor_path)
"""
# Optional: verify what was loaded
print("Recipient files loaded:")
for f, df in zip(csv_files, recipient_df_list):
    print(f"  {os.path.basename(f)} → shape {df.shape}")

print(recipient_df_list[0].head())
print("\nAdvanced donor file loaded:")
print(f"  advanced_donor.csv → shape {advanced_donor_df.shape}")"""

payback_debts_saved = payback_debts_transposed.T
payback_debts= payback_debts_saved






def objective_aprox(w_mismatch, w_distance, w_payback):
    print("Initialize objective function")
    results = []
    organ_list = load_organs(advanced_donor_df)

    for organ in organ_list:

        for recipient_df in recipient_df_list:

            # ordering_priority_7_metaheuristic ALWAYS returns a DataFrame
            result_df = ordering_priority_7_metaheuristic(
                recipient_df,
                organ,
                payback_debts,
                w_mismatch,
                w_distance,
                w_payback
            )

            # result_df is a DataFrame with 1 row
            best = result_df.iloc[0]

            # Safely extract scores — use NaN if missing (happens when there is only 1 ABO-identical match)
            mismatch_score = best["Mismatch_score"] if "Mismatch_score" in best else np.nan
            distance_score = best["Distance_score"] if "Distance_score" in best else np.nan
            equity_score   = best["Equity_score"]   if "Equity_score"   in best else np.nan

            results.append({
                "organ": organ,
                "result_df": result_df,
                "mismatch_score": mismatch_score,
                "distance_score": distance_score,
                "equity_score": equity_score
            })

    # Print results
    """
    for entry in results:
        organ = entry["organ"]
        df = entry["result_df"]

        print("Organ:", organ)
        print("Best recipient dataframe:")
        print(df)

        print("Mismatch score:", entry["mismatch_score"])
        print("Distance score:", entry["distance_score"])
        print("Equity score:", entry["equity_score"])"""

   


    total_mismatch = 0.0
    total_distance = 0.0
    total_equity   = 0.0

    count_mismatch = 0
    count_distance = 0
    count_equity   = 0

    for entry in results:
        ms = entry["mismatch_score"]
        ds = entry["distance_score"]
        es = entry["equity_score"]

        # Mismatch
        if ms is not None and not np.isnan(ms):
            total_mismatch += ms
            count_mismatch += 1

        # Distance
        if ds is not None and not np.isnan(ds):
            total_distance += ds
            count_distance += 1

        # Equity
        if es is not None and not np.isnan(es):
            total_equity += es
            count_equity += 1

    # Compute averages safely
    avg_mismatch = total_mismatch / count_mismatch if count_mismatch > 0 else np.nan
    avg_distance = total_distance / count_distance if count_distance > 0 else np.nan
    avg_equity   = total_equity   / count_equity   if count_equity   > 0 else np.nan
    #avg_distance= max(0, 1 -10*(1-avg_distance))

    """print("=== TOTALS ===")
    print("Total mismatch:", total_mismatch)
    print("Total distance:", total_distance)
    print("Total equity:", total_equity)"""

    print("=== AVERAGES (NaNs skipped) ===")
    print("Average mismatch:", avg_mismatch)
    print("Average distance:", avg_distance)
    print("Average equity:", avg_equity)
    print("Final valuation",avg_mismatch + avg_distance +avg_equity )
    
    
    
    return (avg_mismatch + avg_distance +avg_equity)



def objective_aprox_V2(w_mismatch, w_distance):
    print("Initialize objective function no equity")
    results = []
    organ_list = load_organs(advanced_donor_df)

    for organ in organ_list:

        for recipient_df in recipient_df_list:

            # ordering_priority_7_metaheuristic ALWAYS returns a DataFrame
            result_df = ordering_priority_7_metaheuristic_NO_equity(
                recipient_df,
                organ,
                payback_debts,
                w_mismatch,
                w_distance,
        
            )

            # result_df is a DataFrame with 1 row
            best = result_df.iloc[0]

            # Safely extract scores — use NaN if missing (happens when there is only 1 ABO-identical match)
            mismatch_score = best["Mismatch_score"] if "Mismatch_score" in best else np.nan
            distance_score = best["Distance_score"] if "Distance_score" in best else np.nan
            

            results.append({
                "organ": organ,
                "result_df": result_df,
                "mismatch_score": mismatch_score,
                "distance_score": distance_score,
                
            })

    # Print results
    """
    for entry in results:
        organ = entry["organ"]
        df = entry["result_df"]

        print("Organ:", organ)
        print("Best recipient dataframe:")
        print(df)

        print("Mismatch score:", entry["mismatch_score"])
        print("Distance score:", entry["distance_score"])
        print("Equity score:", entry["equity_score"])"""

   


    total_mismatch = 0.0
    total_distance = 0.0
    

    count_mismatch = 0
    count_distance = 0
    

    for entry in results:
        ms = entry["mismatch_score"]
        ds = entry["distance_score"]
        

        # Mismatch
        if ms is not None and not np.isnan(ms):
            total_mismatch += ms
            count_mismatch += 1

        # Distance
        if ds is not None and not np.isnan(ds):
            total_distance += ds
            count_distance += 1

        

    # Compute averages safely
    avg_mismatch = total_mismatch / count_mismatch if count_mismatch > 0 else np.nan
    avg_distance = total_distance / count_distance if count_distance > 0 else np.nan
    
    #avg_distance= max(0, 1 -10*(1-avg_distance))

    """print("=== TOTALS ===")
    print("Total mismatch:", total_mismatch)
    print("Total distance:", total_distance)
    print("Total equity:", total_equity)"""

    print("=== AVERAGES (NaNs skipped) ===")
    print("Average mismatch:", avg_mismatch)
    print("Average distance:", avg_distance)
    
    print("Final valuation",avg_mismatch + 2*avg_distance  )
    
    
    
    return (avg_mismatch + 2*avg_distance )

