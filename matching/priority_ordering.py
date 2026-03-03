import pandas as pd
from utils.logger import get_matching_logger, log_match, log_match_csv_dynamic
from agents.organs import *
from typing import List
from agents.hospital import *
from collections import Counter
from matching.match_utils import *

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


def ordering_priority_2_to_7(recipient_df, organ: Organ, timestep, verbose=False):
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