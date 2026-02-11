import pandas as pd
from utils.logger import get_matching_logger, log_match, log_match_csv_dynamic
from agents.organs import *
from typing import List
from agents.hospital import *
from collections import Counter
from matching.match_utils import *
from book_keeping.locations import *
from math import radians, sin, cos, sqrt, atan2










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


def ordering_priority_7_metaheuristic(recipient_df, organ: Organ, timestep, verbose=False):
    """After the exchange priority, the original list is sorted by:
    1. ABO identical
    2. Lowest DRB1 mismatches
    3. Lowest A+B mismatches
    4. Longest waiting time (lowest RECIPIENTNUMBER)

    New list:
    1. Use only ABO identical
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

# 2. Calculate all mismatches
    dr_mismatches = []
    a_mismatches = []
    b_mismatches = []

    for _, row in priority_df.iterrows():
        print(type(row["Genomic_HLA-A"])) 
        print(row["Genomic_HLA-A"])
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


# 5. Use these and their coefficient to calculate a score, rank by the score
     # scoring: choose coefficients; example weights
    w_mismatch = 1.0
    w_distance = 1.0
    w_payback = 1.0  # adjust or compute as needed

    # ensure no-length mismatch
    assert len(priority_df) == len(priority_df["Total_mismatches"])

    # compute score, handling NaNs (treat NaN distance as large penalty)
    priority_df["Score"] = (
        w_mismatch * priority_df["Total_mismatches"]
        + w_distance * priority_df["Distance"]
        + w_payback * priority_df["Equity"]
    )
# 6. Sort by score 
    # Sort in descending order (highest score is best)
    priority_df = priority_df.sort_values("Score", ascending=False)

    columns_to_print = ["CITY", "AGE", "ABO_BLOOD_GROUP", "Total_mismatches", "Distance", "Equity", "Score"]
    print(priority_df[columns_to_print].head(5))

    # Find the highest score
    highest_score = priority_df["Score"].max()

    # Filter rows with the highest score
    highest_score_df = priority_df[priority_df["Score"] == highest_score]
    


    # If more than one row has the highest score, use RECIPIENTNUMBER for tiebreaker
    if len(highest_score_df) > 1:
        highest_score_df = highest_score_df.sort_values("RECIPIENTNUMBER", ascending=True)

    # Return the top option
    return highest_score_df.head(1)




#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


def calculate_distance(recipient_df , organ):
    distances = []

    donor_city = organ.city
    lat1, lon1 = CITY_COORDS_LONG_LAT[donor_city]
    
    
    for _, row in recipient_df.iterrows():
       
        recipient_city = row["CITY"]

        lat2, lon2 = CITY_COORDS_LONG_LAT[recipient_city]

        distance = haversine_distance(lat1, lon1, lat2, lon2)
        distances.append(distance)

    if not distances:
        return 0, 0

    return distances

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
"""def calculate_equity_score(priority_df, organ):

    owed_to_df = owed_organs_table_for_donor_city(organ)
    selected_cities, city_row_counts = filter_owed_to_hospitals(organ, owed_to_df)

    for i in range(len(priority_df)):
        city = priority_df.loc[i, "city"]
        
        if city in selected_cities:
            # Get the number of debts for this city from the dictionary
            num_debts = city_row_counts[city]
            
            # Get the population proportion for this city
            city_proportion = city_pop_proportion.get(city, 0)
            
            # Calculate the city score (avoid division by zero)
            city_score = num_debts / city_proportion if city_proportion != 0 else 0
            
            priority_df.loc[i, "Distance_score"] = city_score
        else:
            priority_df.loc[i, "Distance_score"] = 0
    
    return priority_df


def owed_organs_table_for_donor_city(organ):
    donor_city = organ.city
    rows = []
    for hosp in Hospital.registry:
        if donor_city not in hosp.organ_exchange_table.columns:
            continue
        col = hosp.organ_exchange_table[donor_city]  # Series indexed by organ type
        for organ_type, lst in col.items():
            for abo, age in lst:
                rows.append({
                    "OwingHospitalCity": hosp.city,
                    "OrganType": organ_type,
                    "ABO": abo,
                    "Age": age
                })
    df= pd.DataFrame(rows)
    print(df)
    return df

def filter_owed_to_hospitals(organ, owed_df):

    if owed_df.empty:
        print("Warning: Owed organs DataFrame is empty")
        return [], {}
    donor_city = organ.city
    organ_age = organ.donor_age
    organ_ABO = organ.abo_blood

    df = owed_df[owed_df["OwingHospitalCity"].astype(str) != str(donor_city)].reset_index(drop=True)
    if df.empty:
        print("ERROR")
        return [], {}
    age_mask = (df["Age"] > (organ_age - 15)) & (df["Age"] < (organ_age + 15))
    abo_mask = df["ABO"] == organ_ABO

    selected_df = df[age_mask & abo_mask].reset_index(drop=True)

    selected_cities= selected_df["OwingHospitalCity"].unique().tolist()

    city_row_counts = {city: df[df['OwingHospitalCity'] == city].shape[0] for city in selected_cities}

    print(selected_cities)
    print(city_row_counts)
    return selected_cities, city_row_counts
"""

def owed_organs_table_for_donor_city(organ):
    donor_city = organ.city
    rows = []
    for hosp in Hospital.registry:
        if donor_city not in hosp.organ_exchange_table.columns:
            continue
        col = hosp.organ_exchange_table[donor_city]  # Series indexed by organ type
        for organ_type, lst in col.items():
            for abo, age in lst:
                rows.append({
                    "OwingHospitalCity": hosp.city,
                    "OrganType": organ_type,
                    "ABO": abo,
                    "Age": age
                })
    df = pd.DataFrame(rows)
    #print(df)
    return df

def filter_owed_to_hospitals(organ, owed_df):
    # Handle empty DataFrame case
    if owed_df.empty:
        print("Warning: Owed organs DataFrame is empty")
        return [], {}

    donor_city = organ.city
    organ_age = organ.donor_age
    organ_ABO = organ.abo_blood

    # Ensure donor_city is a string and handle potential NaN values
    df = owed_df[owed_df["OwingHospitalCity"].astype(str) != str(donor_city)].reset_index(drop=True)
    
    # If filtering by donor city results in an empty DataFrame
    if df.empty:
        print("Warning: No hospitals owe organs after filtering out donor city")
        return [], {}

    # Add filtering steps with error handling
    try:
        age_mask = (df["Age"] > (organ_age - 15)) & (df["Age"] < (organ_age + 15))
        abo_mask = df["ABO"] == organ_ABO

        selected_df = df[age_mask & abo_mask].reset_index(drop=True)

        # Handle case when no cities match the criteria
        if selected_df.empty:
            print("Warning: No hospitals match age and ABO criteria")
            return [], {}

        selected_cities = selected_df["OwingHospitalCity"].unique().tolist()

        # Count rows for each selected city in the original filtered dataframe
        city_row_counts = {city: df[df['OwingHospitalCity'] == city].shape[0] for city in selected_cities}

        print("Selected Cities:", selected_cities)
        print("City Row Counts:", city_row_counts)
        
        return selected_cities, city_row_counts

    except Exception as e:
        print(f"Error in filtering owed hospitals: {e}")
        return [], {}

def calculate_equity_score(priority_df, organ):
    # Ensure the input is a DataFrame
    if not isinstance(priority_df, pd.DataFrame):
        raise TypeError("priority_df must be a pandas DataFrame")

    # Reset index to ensure consecutive integer indexing
    priority_df = priority_df.reset_index(drop=True)

    # Handle potential empty DataFrame from owed_organs_table_for_donor_city
    owed_to_df = owed_organs_table_for_donor_city(organ)
    
    # If owed_to_df is empty, set all Distance_scores to 0
    if owed_to_df.empty:
        priority_df = priority_df.copy()
        priority_df["Equity"] = 0
        return priority_df

    # Proceed with filtering and scoring
    selected_cities, city_row_counts = filter_owed_to_hospitals(organ, owed_to_df)

    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    priority_df = priority_df.copy()

    # Ensure Distance_score column exists
    if "Equity" not in priority_df.columns:
        priority_df["Equity"] = 0.0

    # Use iterrows() for more robust iteration
    for index, row in priority_df.iterrows():
        city = row["CITY"]
        
        # Check if city is in selected_cities and city exists in population proportion
        if city in selected_cities and city in city_pop_proportion:
            # Get the number of debts for this city from the dictionary
            num_debts = city_row_counts.get(city, 0)
            
            # Get the population proportion for this city
            city_proportion = city_pop_proportion[city]
            
            # Calculate the city score (avoid division by zero)
            city_score = num_debts / city_proportion if city_proportion != 0 else 0
            
            priority_df.loc[index, "Equity"] = city_score
        else:
            priority_df.loc[index, "Equity"] = 0
    
    return priority_df


