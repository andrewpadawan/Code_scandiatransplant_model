import pandas as pd
from utils.logger import get_matching_logger, log_match, log_match_csv_dynamic
from agents.organs import *
from typing import List
from agents.hospital import *
from collections import Counter
from matching.match_utils import *
from book_keeping.locations import *
from math import radians, sin, cos, sqrt, atan2


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

def all_organ_debts():
    rows = []

    for hosp in Hospital.registry:
        table = hosp.organ_exchange_table

        # Iterate over every city column
        for receiving_city in table.columns:

            # Each column contains a Series indexed by organ type
            obligations = table[receiving_city]

            for organ_type, owed_list in obligations.items():
                for abo, age in owed_list:
                    rows.append({
                        "OwingHospitalCity": hosp.city,
                        "ReceivingHospitalCity": receiving_city,
                        "OrganType": organ_type,
                        "ABO": abo,
                        "Age": age
                    })

    return pd.DataFrame(rows)

"""
def owed_by_organs_table(organ):
    donor_city = organ.city
    rows = []

    # Find the hospital corresponding to the donor city
    donor_hospital = None
    for hosp in Hospital.registry:
        if hosp.city == donor_city:
            donor_hospital = hosp
            break

    if donor_hospital is None:
        return pd.DataFrame()  # donor city not found

    # donor_hospital.organ_exchange_table:
    # columns = cities donor_city owes TO
    # rows    = organ types
    for receiving_city in donor_hospital.organ_exchange_table.columns:
        obligations = donor_hospital.organ_exchange_table[receiving_city]

        for organ_type, owed_list in obligations.items():
            for abo, age in owed_list:
                rows.append({
                    "ReceivingHospitalCity": receiving_city,
                    "OrganType": organ_type,
                    "ABO": abo,
                    "Age": age
                })
    print("Owes")
    print(pd.DataFrame(rows))
    return pd.DataFrame(rows)"""

"""
def compute_city_equity_scores(owed_to_df, owes_df, donor_city):
    # Start with all cities in the system, all with score 0
    scores = {city: 0 for city in city_country_map.keys()}

    # 1. Hospitals that OWE TO donor_city
    #    - They get -1 per organ
    #    - Donor city gets +1 per organ
    if not owed_to_df.empty:
        for city in owed_to_df["OwingHospitalCity"]:
            scores[city] -= 1
        scores[donor_city] += len(owed_to_df)

    # 2. Hospitals the donor city OWES organs TO
    #    - They get +1 per organ
    #    - Donor city gets -1 per organ
    if not owes_df.empty:
        for city in owes_df["ReceivingHospitalCity"]:
            scores[city] += 1
        scores[donor_city] -= len(owes_df)

    # Normalize by population proportion
    normalized_scores = {}
    for city, score in scores.items():
        pop = city_pop_proportion.get(city, None)
        if pop is None or pop == 0:
            raise
        else:
            normalized_scores[city] = score / pop

    # Convert to DataFrame
    result_df = pd.DataFrame(
        [{"HospitalCity": city, "Score": normalized_scores[city]}
         for city in city_country_map.keys()]
    )
    
    return result_df"""
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


def calculate_equity_score(priority_df, organ):
    if not isinstance(priority_df, pd.DataFrame):
        raise TypeError("priority_df must be a pandas DataFrame")

    priority_df = priority_df.reset_index(drop=True)

    # Compute obligations
    organ_debts= all_organ_debts()
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
