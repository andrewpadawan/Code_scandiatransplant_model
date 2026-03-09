import pandas as pd
from utils.logger import get_matching_logger, log_match, log_match_csv_dynamic
from agents.organs import *
from typing import List
from agents.hospital import *
from collections import Counter
from matching.match_utils import *
from book_keeping.locations import *
from math import radians, sin, cos, sqrt, atan2
from matching.metaheuristics import calculate_distance

#AUX functions that i need to modify

def compute_city_equity_scores(all_debts_df):

    # Start with all cities at 0
    scores = {city: 0 for city in city_country_map.keys()}

    # If no debts exist, return zeros immediately
    if all_debts_df.empty:
        return pd.DataFrame({
            "HospitalCity": list(scores.keys()),
            "Score": [0.0] * len(scores)
        })

    # -1 for each organ a city owes
    for city in all_debts_df["OwingHospitalCity"]:
        scores[city] -= 1

    # +1 for each organ a city receives
    for city in all_debts_df["ReceivingHospitalCity"]:
        scores[city] += 1

    # Normalize by population proportion
    normalized_scores = {}
    for city, score in scores.items():
        pop = city_pop_proportion[city]
        normalized_scores[city] = score / pop

    return pd.DataFrame({
        "HospitalCity": list(normalized_scores.keys()),
        "Score": list(normalized_scores.values())
    })


def calculate_equity_score(priority_df, organ, payback_debts):
    if not isinstance(priority_df, pd.DataFrame):
        raise TypeError("priority_df must be a pandas DataFrame")

    priority_df = priority_df.reset_index(drop=True)

    # Compute obligations
    organ_debts= all_organ_debts_from_df(payback_debts)
    #
    #print(organ_debts.head())

    # Compute city-level equity scores
    equity_df = compute_city_equity_scores(organ_debts)

    # Merge equity scores into priority_df
    priority_df = priority_df.merge(
        equity_df,
        left_on="CITY",
        right_on="HospitalCity",
        how="left"
    )

    # Rename and clean up
    priority_df = priority_df.rename(columns={"Score": "Equity_score"})
    priority_df = priority_df.drop(columns=["HospitalCity"])

    return priority_df

def all_organ_debts_from_df(payback_debts):

    rows = []

    # Rows = owing hospitals
    for owing_city in payback_debts.index:

        # Columns = receiving hospitals
        for receiving_city in payback_debts.columns:

            owed_list = payback_debts.loc[owing_city, receiving_city]

            # Each cell contains a list of tuples like: [("O", 62)]
            for abo, age in owed_list:
                rows.append({
                    "OwingHospitalCity": owing_city,
                    "ReceivingHospitalCity": receiving_city,
                    "OrganType": "kidney",   # your matrix is kidney-only
                    "ABO": abo,
                    "Age": age
                })

    return pd.DataFrame(rows)


#]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]] ORDERING FUNCTION
def ordering_priority_7_metaheuristic(recipient_df, organ: Organ,payback_debts, w_mismatch= 1.0,w_distance=1.0,w_payback=1.0, verbose=False):

    """After the exchange priority, the original list is sorted by:
    1. ABO identical
    2. Lowest DRB1 mismatches
    3. Lowest A+B mismatches
    4. Longest waiting time (lowest RECIPIENTNUMBER)

    New list:
    1. Use only ABO identical
    ! Only is negative crossmatch
    2. Calculate all mismatches
    3. Calculate all distances
    4. calculate equity by means of payback debt
    5. calculate a score and sort by it
    6. If still more than one, sort by time on waiting list
    """

# 1) use only ABO identical if there are any to keep the ordering consistent with SCTP rules
    if recipient_df.empty:
        print("Empty!!")
    priority_df = recipient_df

    if len(priority_df) == 1:
        
        return priority_df

# 2. Calculate all mismatches
    dr_mismatches = []
    a_mismatches = []
    b_mismatches = []

    for _, row in priority_df.iterrows():
        #print(type(row["Genomic_HLA-A"])) 
        #print(row["Genomic_HLA-A"])
        dr_mismatches.append(count_mismatches(organ.geno_HLA_DRB1, row["Genomic_HLA-DRB1"]))
        a_mismatches.append(count_mismatches(organ.geno_HLA_A, row["Genomic_HLA-A"]))
        b_mismatches.append(count_mismatches(organ.geno_HLA_B, row["Genomic_HLA-B"]))

    priority_df = priority_df.copy()
    priority_df["DRB1_mismatches"] = dr_mismatches
    priority_df["AB_mismatches"] = [a + b for a, b in zip(a_mismatches, b_mismatches)]
    total_mismatches= [d + a + b for d, a, b in zip(dr_mismatches, a_mismatches, b_mismatches)]
    priority_df["Total_mismatches"] = total_mismatches

# 3. Calculate all distances
    distances= calculate_distance(priority_df, organ)
    priority_df["Distance"] = distances

# 4. calculate equity by means of payback debt 

    priority_df=calculate_equity_score(priority_df, organ, payback_debts)
    equity_raw = priority_df["Equity_score"]
    max_abs = equity_raw.abs().max()

    if max_abs > 0:
        priority_df["Equity_scaled"] = equity_raw / float(max_abs) #To normalize
    else:
        priority_df["Equity_scaled"] = 0.0
    #print("max_abs")
    #print(max_abs)



    equity_score= priority_df['Equity_scaled']
    #print("equity score")
    #print(equity_score)

# 5. Use these and their coefficient to calculate a score, rank by the score
     # scoring: choose coefficients; example weights
     # adjust or compute as needed

    # ensure no-length mismatch
    assert len(priority_df) == len(priority_df["Total_mismatches"])

    #mismatch score (1 if zero mismatches, 0 if 6 mismatches)
    #print(type(priority_df["Total_mismatches"][0]))
    mismatch_score= 1-(priority_df["Total_mismatches"]/6.0)
    priority_df["Mismatch_score"]= mismatch_score.astype(float)
    #print(mismatch_score)
    #distance score (0 if max distance travelled, 0 if local) Max distance is Reykjavik to Tartu
    max_distance= 5442.19
    distance_score= 1- (priority_df["Distance"]/max_distance)
    priority_df["Distance_score"]= distance_score.astype(float)




    # compute score, handling NaNs (treat NaN distance as large penalty)
    priority_df["Score"] = (
        w_mismatch * mismatch_score
        + w_distance * distance_score
        + w_payback * equity_score
    )
    
   
    #print(priority_df["Score"][0:10])
    
# 6. Sort by score 
    # Sort in descending order (highest score is best)
    priority_df = priority_df.sort_values("Score", ascending=False)
    if verbose:
        columns_to_print = ["RECIPIENTNUMBER", "CITY", "Total_mismatches", "Mismatch_score", "Distance","Distance_score", "Equity_score","Equity_scaled", "Score"]
        print("sorted by score")
        print(priority_df[columns_to_print].head(5))

    # Find the highest score
    highest_score = priority_df["Score"].max()

    # Filter rows with the highest score
    highest_score_df = priority_df[priority_df["Score"] == highest_score]
    


    # If more than one row has the highest score, use RECIPIENTNUMBER for tiebreaker
    if len(highest_score_df) > 1:
        highest_score_df = highest_score_df.sort_values("RECIPIENTNUMBER", ascending=True)
        #print("selected highest score")
    #print(highest_score_df.head(5))
    # Return the top option
  
    return highest_score_df.head(1)



def ordering_priority_7_metaheuristic_NO_equity(recipient_df, organ: Organ,payback_debts, w_mismatch= 1.0,w_distance=1.0, verbose=False):

    """After the exchange priority, the original list is sorted by:
    1. ABO identical
    2. Lowest DRB1 mismatches
    3. Lowest A+B mismatches
    4. Longest waiting time (lowest RECIPIENTNUMBER)

    New list:
    1. Use only ABO identical
    ! Only is negative crossmatch
    2. Calculate all mismatches
    3. Calculate all distances
    4. calculate equity by means of payback debt
    5. calculate a score and sort by it
    6. If still more than one, sort by time on waiting list
    """

# 1) use only ABO identical if there are any to keep the ordering consistent with SCTP rules
    if recipient_df.empty:
        print("Empty!!")
    priority_df = recipient_df

    if len(priority_df) == 1:
        
        return priority_df

# 2. Calculate all mismatches
    dr_mismatches = []
    a_mismatches = []
    b_mismatches = []

    for _, row in priority_df.iterrows():
        #print(type(row["Genomic_HLA-A"])) 
        #print(row["Genomic_HLA-A"])
        dr_mismatches.append(count_mismatches(organ.geno_HLA_DRB1, row["Genomic_HLA-DRB1"]))
        a_mismatches.append(count_mismatches(organ.geno_HLA_A, row["Genomic_HLA-A"]))
        b_mismatches.append(count_mismatches(organ.geno_HLA_B, row["Genomic_HLA-B"]))

    priority_df = priority_df.copy()
    priority_df["DRB1_mismatches"] = dr_mismatches
    priority_df["AB_mismatches"] = [a + b for a, b in zip(a_mismatches, b_mismatches)]
    total_mismatches= [d + a + b for d, a, b in zip(dr_mismatches, a_mismatches, b_mismatches)]
    priority_df["Total_mismatches"] = total_mismatches

# 3. Calculate all distances
    distances= calculate_distance(priority_df, organ)
    priority_df["Distance"] = distances

# 4. calculate equity by means of payback debt 





    
    #print("equity score")
    #print(equity_score)

# 5. Use these and their coefficient to calculate a score, rank by the score
     # scoring: choose coefficients; example weights
     # adjust or compute as needed

    # ensure no-length mismatch
    assert len(priority_df) == len(priority_df["Total_mismatches"])

    #mismatch score (1 if zero mismatches, 0 if 6 mismatches)
    #print(type(priority_df["Total_mismatches"][0]))
    mismatch_score= 1-(priority_df["Total_mismatches"]/6.0)
    priority_df["Mismatch_score"]= mismatch_score.astype(float)
    #print(mismatch_score)
    #distance score (0 if max distance travelled, 0 if local) Max distance is Reykjavik to Tartu
    max_distance= 5442.19
    
    distance_score= 1- ((priority_df["Distance"])/max_distance)

    priority_df["Distance_score"]= distance_score.astype(float)




    # compute score, handling NaNs (treat NaN distance as large penalty)
    priority_df["Score"] = (
        w_mismatch * mismatch_score
        + w_distance * distance_score
        
    )
    
   
    #print(priority_df["Score"][0:10])
    
# 6. Sort by score 
    # Sort in descending order (highest score is best)
    priority_df = priority_df.sort_values("Score", ascending=False)
    if verbose:
        columns_to_print = ["RECIPIENTNUMBER", "CITY", "Total_mismatches", "Mismatch_score", "Distance","Distance_score",  "Score"]
        print("sorted by score")
        print(priority_df[columns_to_print].head(5))

    # Find the highest score
    highest_score = priority_df["Score"].max()

    # Filter rows with the highest score
    highest_score_df = priority_df[priority_df["Score"] == highest_score]
    


    # If more than one row has the highest score, use RECIPIENTNUMBER for tiebreaker
    if len(highest_score_df) > 1:
        highest_score_df = highest_score_df.sort_values("RECIPIENTNUMBER", ascending=True)
        #print("selected highest score")
    #print(highest_score_df.head(5))
    # Return the top option
  
    return highest_score_df.head(1)
