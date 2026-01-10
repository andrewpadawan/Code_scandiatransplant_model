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





"""
OLDdef ordering_priority_2_to_7(recipient_df, organ:Organ, timestep, verbose= False):
    After the exchange priority, the list is as default sorted in the order of 
matching AB0, followed by lowest number of DR mismatches, followed by 
lowest number of AB mismatches and the waiting time. 
All priority 6 and 7 patients that are AB0 compatibility will appear
#At each step, check if more than one of the recipients covers the condition, and if so, continue. If not, return that recipient
    if verbose:
         print("Considered for ordering: ")
         print(recipient_df)
    ABO_identical_df= ABO_identical(organ, recipient_df)
    if not ABO_identical_df.empty:
        if len(ABO_identical_df) == 1:
            return ABO_identical_df
        else:
            priority_df=ABO_identical_df
    else:
        priority_df=recipient_df
    
    organ_hla_a_set= set(organ.geno_HLA_A)
    organ_hla_b_set= set(organ.geno_HLA_B)
    organ_hla_DR_set= set(organ.geno_HLA_DRB1)

   
#calculate mismatches (DRB1, A, B) and store into the priority_df
   
    dr_mismatches = []
    a_mismatches  = []
    b_mismatches  = []

    for idx, row in priority_df.iterrows():
        recipient_hla_DR_set = set(row["Genomic_HLA-DRB1"])
        recipient_hla_a_set  = set(row["Genomic_HLA-A"])
        recipient_hla_b_set  = set(row["Genomic_HLA-B"])

        dr_mismatches.append(len(organ_hla_DR_set - recipient_hla_DR_set))
        a_mismatches.append(len(organ_hla_a_set - recipient_hla_a_set))
        b_mismatches.append(len(organ_hla_b_set - recipient_hla_b_set))

    priority_df = priority_df.copy()
    priority_df.loc[:, "DRB1_mismatches"] = dr_mismatches
    priority_df.loc[:, "AB_mismatches"] = [a + b for a, b in zip(a_mismatches, b_mismatches)]
    
    if verbose:
         print("Df considered for ordering after mismatch check")
         print(priority_df)
#check DRB1 mismatches
    min_drb1 = priority_df["DRB1_mismatches"].min() 
    # Filter DataFrame to only those recipients with that value 
    lowest_drb1_df = priority_df[priority_df["DRB1_mismatches"] == min_drb1]
    if len(lowest_drb1_df) == 1:
            return lowest_drb1_df
    else:
            priority_df=lowest_drb1_df
#check AB mismatches
    min_ab = priority_df["AB_mismatches"].min() 
    lowest_ab_df = priority_df[priority_df["AB_mismatches"] == min_ab]
    if len(lowest_ab_df) == 1:
            return lowest_ab_df
    else:
            priority_df=lowest_ab_df

#filter by time on the waiting list, use RECIPIENTNUMBER as a proxy
    priority_df_id_sorted = priority_df.sort_values("RECIPIENTNUMBER", ascending=True)
    top_recipient = priority_df_id_sorted.head(1)
    # Return a DataFrame of all valid recipients
    return top_recipient
"""


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
        dr_mismatches.append(count_mismatches(organ.geno_HLA_DRB1, row["Genomic_HLA-DRB1"]))
        a_mismatches.append(count_mismatches(organ.geno_HLA_A, row["Genomic_HLA-A"]))
        b_mismatches.append(count_mismatches(organ.geno_HLA_B, row["Genomic_HLA-B"]))

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