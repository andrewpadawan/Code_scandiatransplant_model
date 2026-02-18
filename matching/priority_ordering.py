import pandas as pd
from utils.logger import get_matching_logger, log_match, log_match_csv_dynamic
from agents.organs import *
from typing import List
from agents.hospital import *
from collections import Counter
from matching.match_utils import *
from book_keeping.locations import *
from math import radians, sin, cos, sqrt, atan2
from matching.metaheuristics import *


def ordering_priority_1(recipient_df, organ:Organ, timestep, verbose=False):
    """ If there is more than one STAMP candidate when doing the search for kidney exchange obligations the recipients must be prioritised in the following order 
    1. Lowest TS, ABO compatible
    2. ABO identical recipients
    3. Same country as donor
    4. Longest waiting time
    The search result list is sorted by a calculated AMP-score, which is a weight score based on these priorities.
    """
    """
    From email from Ilse
    1. 6000+(-2000*TS, ABO compatible)
    +
    2. ABO identical +50, all others 0
    +
    3. Same recipient-donor country +25, all others 0
    +
    4. Wt months/100
      
    
    """
    if verbose:
         print("For priority 1")
         print(recipient_df)
    all_scores= {}
    for _, recipient_row in recipient_df.iterrows():
        recipient_ID= recipient_row["RECIPIENTNUMBER"]
        all_scores[recipient_ID]= calculate_AMP_score(recipient_row, organ, timestep)
    if verbose:
         print(all_scores)
    best_recipient_id, best_score = max(all_scores.items(), key=lambda x: x[1]) 
    # Filter the DataFrame to only that recipient 
    best_recipient_df = recipient_df[recipient_df["RECIPIENTNUMBER"]== best_recipient_id]
    return best_recipient_df




def ordering_priority_2_to_5(recipient_df, organ: Organ, timestep, verbose=False):
    """After the exchange priority, the list is sorted by:
    1. ABO identical
    2. Lowest DRB1 mismatches
    3. Lowest A+B mismatches
    4. Longest waiting time (lowest RECIPIENTNUMBER)
    """
    if verbose:
        print("Considered for ordering:")
        print(recipient_df)

    ABO_identical_df = ABO_identical(organ, recipient_df)
    priority_df = ABO_identical_df if not ABO_identical_df.empty else recipient_df

    if len(priority_df) == 1:
        return priority_df

    dr_mismatches = []
    a_mismatches = []
    b_mismatches = []

    for _, row in priority_df.iterrows():
        dr_mismatches.append(count_mismatches(organ.sero_HLA_DRB1, row["Serologic_HLA-DRB1"]))
        a_mismatches.append(count_mismatches(organ.sero_HLA_A, row["Serologic_HLA-A"]))
        b_mismatches.append(count_mismatches(organ.sero_HLA_B, row["Serologic_HLA-B"]))

    priority_df = priority_df.copy()
    priority_df["DRB1_mismatches"] = dr_mismatches
    priority_df["AB_mismatches"] = [a + b for a, b in zip(a_mismatches, b_mismatches)]

    if verbose:
        print("Df considered for ordering after mismatch check:")
        print(priority_df)

    # Step 1: Filter by lowest DRB1 mismatches
    min_drb1 = priority_df["DRB1_mismatches"].min()
    priority_df = priority_df[priority_df["DRB1_mismatches"] == min_drb1]
    if len(priority_df) == 1:
        return priority_df

    # Step 2: Filter by lowest A+B mismatches
    min_ab = priority_df["AB_mismatches"].min()
    priority_df = priority_df[priority_df["AB_mismatches"] == min_ab]
    if len(priority_df) == 1:
        return priority_df

    # Step 3: Sort by waiting time (proxy: RECIPIENTNUMBER)
    priority_df = priority_df.sort_values("RECIPIENTNUMBER", ascending=True)
    return priority_df.head(1)

#Auxiliary functions for ordering 

def calculate_AMP_score(recipient_row, organ, timestep):
    score= 0
    if is_ABO_compatible(recipient_row, organ):
        score= score + 6000- 2000*recipient_row["TS"]
    if is_ABO_identical(recipient_row, organ):
        score= score + 50
    if is_same_country(recipient_row, organ):
        score= score + 25

    months_waited= calculate_waited_months(recipient_row, timestep)
    score= score + (months_waited/100)
    return score


def calculate_waited_months(recipient_row, timestep):
    days_on_wl= timestep - recipient_row["TIMESTEP_ENTERED"]
    months_on_wl= days_on_wl/30
    return months_on_wl


def ordering_priority_7_metaheuristic(recipient_df, organ: Organ, timestep,w_mismatch= 1.0,w_distance=1.0,w_payback=1.0, verbose=True):

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
    ABO_identical_df = ABO_identical(organ, recipient_df)
    priority_df = ABO_identical_df if not ABO_identical_df.empty else recipient_df

    if len(priority_df) == 1:
        return priority_df
# b) Only keep if negative crossmatch
    negative_crossmatch_df = priority_df[ ~priority_df.apply(lambda row: virtual_crossmatch(row, organ), axis=1) ]
    #IF NEGATIVEcrossmatch is empty so will be priority_df, function returns empty df
    priority_df = negative_crossmatch_df 

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
    priority_df=calculate_equity_score(priority_df, organ)
    equity_raw = priority_df["Equity_score"]
    max_abs = equity_raw.abs().max()

    if max_abs > 0:
        priority_df["Equity_scaled"] = equity_raw / float(max_abs)
    else:
        priority_df["Equity_scaled"] = 0.0
    print("max_abs")
    print(max_abs)



    equity_score= priority_df['Equity_scaled']
    print("equity score")
    print(equity_score)

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
    
   
    print(priority_df["Score"][0:10])
    
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
        print("selected highest score")
    print(highest_score_df.head(5))
    # Return the top option
    return highest_score_df.head(1)




#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


