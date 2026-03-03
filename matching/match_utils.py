import pandas as pd
from utils.logger import get_matching_logger, log_match, log_match_csv_dynamic
from agents.organs import *
from typing import List
from agents.hospital import *
import random
import numpy as np
from collections import Counter

import ast
from patient_generators.generating_constants import *
abo_compatibility = {
    "O": ["O", "A", "B", "AB"],
    "A": ["A", "AB"],
    "B": ["B", "AB"],
    "AB": ["AB"]
}
dict_abo_identical_priority_2_to_5 = {
    #must be abo indetical except donors A can be exchnaged to recipients of blood AB
    "O": ["O"],
    "A": ["A", "AB"],
    "B": ["B"],
    "AB": ["AB"]
}


def abo_identical_priority_2_to_5( recipient_df, organ:Organ):
#Exchange obligation priority 2-5: Donors are matched ABO-identical, with the exception of donors 
#of blood group A, which also can be exchanged to recipients of blood group AB.
    
    organ_abo= organ.abo_blood
   
    identical_types = dict_abo_identical_priority_2_to_5.get(organ_abo, [])
    identical_recipients = recipient_df[
        recipient_df["ABO_BLOOD_GROUP"].isin(identical_types)
            ]
    if not identical_recipients.empty:
        return identical_recipients
    return pd.DataFrame()
    




def filter_priority_4_compatible(organ:Organ, recipient_df, verbose):
     #If there are no udner 16 recipients it does not apply
    under_16= recipient_df[recipient_df["AGE"] < 16]
    if under_16.empty:
        return recipient_df.iloc[0:0]

    valid_indices_DRB1= []
    valid_indices= []
    # if there is HLA-DRB1 compatibility and in addition not more than 2 HLA-A, B mismatches. 
    
    # Filter recipients: DRB1 compatible, so no mismatches
    for idx, recipient_row in under_16.iterrows(): 

        dr_mismatches= count_mismatches(organ.sero_HLA_DRB1, recipient_row["Serologic_HLA-DRB1"])
        if dr_mismatches== 0:
            valid_indices_DRB1.append(idx)
        

    compatible_DRB1_df= under_16.loc[valid_indices_DRB1]

    #calculate mismatches (no more than 2 in HLA A and B)
    for idx, recipient_row in compatible_DRB1_df.iterrows(): 

        a_mismatch= count_mismatches(organ.sero_HLA_A, recipient_row["Serologic_HLA-A"])
        b_mismatch= count_mismatches(organ.sero_HLA_B, recipient_row["Serologic_HLA-B"])

        if a_mismatch + b_mismatch > 2:
            continue

        valid_indices.append(idx)

    # Return a DataFrame of all valid recipients
    return compatible_DRB1_df.loc[valid_indices]



def parse_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        return ast.literal_eval(x)
    return []


def filter_HLA_priority_1(organ:Organ, recipient_df, verbose= False):
    donor_alleles_raw = [
        organ.geno_HLA_A,
        organ.geno_HLA_B,
        organ.geno_HLA_C,
        organ.geno_HLA_DRB1,
        organ.geno_HLA_DQA1,
        organ.geno_HLA_DQB1,
        organ.geno_HLA_DPA1,
        organ.geno_HLA_DPB1,
    ]
    # Flatten into a single list of alleles 
    donor_alleles = [] 
    for item in donor_alleles_raw:
        donor_alleles.extend(parse_list(item))
    if verbose:
        print("!!!!!!!!!!!!!!!!HLA priority 1 filtering")
        print(donor_alleles)
        print(type(donor_alleles))
        print(donor_alleles[0])
    # Filter recipients: compatible if none of the donor alleles are in their antibody list
    recipient_df["HLA_antibodies"] = recipient_df["HLA_antibodies"].apply(parse_list)

    mask = recipient_df["HLA_antibodies"].apply(
    lambda antibodies: not any(a in donor_alleles for a in antibodies))

    if verbose:
        print(mask)
    filtered_df = recipient_df[mask]

    #compatible_df= sample_rows(filtered_df)
    
    return filtered_df

    
def filter_HLA_A_B_DRB1_compatible(organ:Organ, recipient_df):

    valid_indices= []
    

    for idx, recipient_row in recipient_df.iterrows():

        mismatches_a = count_mismatches(organ.sero_HLA_A, recipient_row["Serologic_HLA-A"])
        mismatches_b = count_mismatches(organ.sero_HLA_B, recipient_row["Serologic_HLA-B"])
        mismatches_dr = count_mismatches(organ.sero_HLA_DRB1, recipient_row["Serologic_HLA-DRB1"])
        mismatches= mismatches_a + mismatches_b+ mismatches_dr

        if mismatches > 0:
            continue
        
        
        #if organ.bw4_6 != recipient_row["Calculated Bw4/BW6"]:
            #continue

        valid_indices.append(idx)

    # Return a DataFrame of all valid recipients
    return recipient_df.loc[valid_indices]  



# Helping functions
def rank_abo_identical(organ:Organ, recipient_df):
    filtered_df = recipient_df[recipient_df["ABO_BLOOD_GROUP"] == organ.abo_blood]
    owed_cities= check_payback(organ)
    if owed_cities:
        filtered_df = filtered_df[filtered_df["CITY"].isin(owed_cities)]

    ranked_identical = filtered_df.sort_values(by="RECIPIENTNUMBER")

    if not ranked_identical.empty:
        return ranked_identical
    #return only the best match (?)
    return pd.DataFrame()

def rank_abo_compatible(organ, recipient_df):
    organ_abo= organ.abo_blood
    owed_cities= check_payback(organ)
    compatible_types = abo_compatibility.get(organ_abo, [])
    compatible_recipients = recipient_df[
        recipient_df["ABO_BLOOD_GROUP"].isin(compatible_types)
            ]

    if owed_cities:
        compatible_recipients = compatible_recipients[compatible_recipients["CITY"].isin(owed_cities)]

    ranked_compatible= compatible_recipients.sort_values(by="RECIPIENTNUMBER")
    if not ranked_compatible.empty:
        return ranked_compatible
    return pd.DataFrame()


def check_payback(organ:Organ):
    #Simpliefied, its not checking that the organ is of the same quality
    hospital_city= organ.city
    organ_type = organ.type
    hospital = next(
            (h for h in Hospital.registry if h.city == hospital_city),
            None
        )
    
    try:
        payback_row = hospital.organ_exchange_table.loc[organ_type]
    except KeyError:
        return {}

    # Filter cities where this hospital owes organs (positive values)
    owed_cities = [city for city, count in payback_row.items() if count > 0]
    return owed_cities

def log_payback(recipient_df, organ):
    recipient_series = recipient_df.iloc[0]
    recipient_hos = next(
            (h for h in Hospital.registry if h.city == recipient_series["CITY"]),
            None
        )
    donating_hos= next(
        (h for h in Hospital.registry if h.city == organ.city),
        None
    )
    recipient_hos.organ_exchange_table.loc[organ.type, organ.city] += 1
    donating_hos.organ_exchange_table.loc[organ.type, recipient_series["CITY"]] -= 1

def log_debt_payback_ABO_age(recipient_df, organ):
    owed_city = organ.city
    organ_abo = organ.abo_blood
    organ_age = organ.donor_age
    recipient_series = recipient_df.iloc[0]

    # Find the hospital that RECEIVED the organ (and now owes payback)
    indebted_hos = next(
        (h for h in Hospital.registry if h.city == recipient_series["CITY"]),
        None
    )

    if indebted_hos is None:
        return

    # Get the existing list for this organ type and owed city
    cell_list = indebted_hos.organ_exchange_table.at[organ.type, owed_city]

    # Append the tuple (ABO, age)
    cell_list.append((organ_abo, organ_age))



def check_STAMP_status(recipient_row):
    return recipient_row["TS"] <= 0.02


def is_ABO_compatible(recipient_row, organ):
    organ_abo = organ.abo_blood
    compatible_types = abo_compatibility.get(organ_abo, [])
    
    return recipient_row["ABO_BLOOD_GROUP"] in compatible_types

def is_ABO_identical(recipient_row, organ): 
    """ Return True if the recipient row is ABO identical to the organ. Safe: uses .get so missing column won't raise. """ 
    return recipient_row.get("ABO_BLOOD_GROUP") == getattr(organ, "abo_blood", None)

def ABO_compatible_df(recipient_df, organ):
    organ_abo= organ.abo_blood
    
    compatible_types = abo_compatibility.get(organ_abo, [])
    compatible_recipients = recipient_df[
        recipient_df["ABO_BLOOD_GROUP"].isin(compatible_types)
            ]
    return compatible_recipients

def ABO_identical(organ:Organ, recipient_df):
    filtered_df = recipient_df[recipient_df["ABO_BLOOD_GROUP"] == organ.abo_blood]
    if not filtered_df.empty:
        return filtered_df
    #return only the best match (?)
    return pd.DataFrame()


def is_same_country(recipient_row, organ):
    """ Return True if the recipient_row's COUNTRY matches organ.country. Safe: handles missing values and does a case-insensitive, whitespace-trimmed comparison. """ 
    # read values safely 
    row_country = recipient_row.get("COUNTRY") 
    organ_country = getattr(organ, "country", None) 
    if row_country is None or organ_country is None: 
        return False # normalize and compare 
    try: 
        return str(row_country).strip().upper() == str(organ_country).strip().upper() 
    except Exception: 
        return False
    
    

def count_mismatches(donor_alleles, recipient_alleles, verbose= False):
    donor = parse_serologic_list(donor_alleles)
    recipient = parse_serologic_list(recipient_alleles)

    if verbose:
        print("Donor:", donor)
        print(type(donor))
        print("Recipient:", recipient)
        print(type(recipient))

    mismatches = 0
    for a in donor:
        if verbose:
            print(a)
        if a not in recipient:
            mismatches += 1
    if verbose:
        print("Mismatches:", mismatches)

    return mismatches



def parse_serologic_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        x = x.strip().strip("[]")
        parts = [p.strip().strip("'").strip('"') for p in x.split(",")]
        return [p for p in parts if p]
    return []



def virtual_crossmatch(recipient_row, organ, verbose= False):
    donor_alleles_raw = [
        organ.geno_HLA_A,
        organ.geno_HLA_B,
        organ.geno_HLA_C,
        organ.geno_HLA_DRB1,
        organ.geno_HLA_DQA1,
        organ.geno_HLA_DQB1,
        organ.geno_HLA_DPA1,
        organ.geno_HLA_DPB1,
    ]

    # Flatten into a single list of alleles 
    donor_alleles = [] 
    for item in donor_alleles_raw:
        donor_alleles.extend(parse_list(item))

    if verbose:
        print("!!!!!!!!!!!!!!!!HLA VIRTUAL CROSSMATCH")
        print(donor_alleles)
        print(type(donor_alleles))
        
    # Filter recipients: compatible if none of the donor alleles are in their antibody list
    recipient_antibodies = parse_list(recipient_row["HLA_antibodies"])
    #TRanslate to sero
    sero_recipient_antibodies= translate_lowres_to_serologic(recipient_antibodies, hla_to_serologic)

    if verbose: 
        print("Recipient antibodies geno:", recipient_antibodies)
        print("Recipient antibodies sero:", sero_recipient_antibodies)

    #positive crossmatch if any antibody matches any donor allele 
    positive = any(a in donor_alleles for a in sero_recipient_antibodies)

    if verbose: 
        print("Virtual crossmatch positive?" , positive) 
        
    return positive


def translate_lowres_to_serologic(allele_list, mapping):
    sero_list = []

    for allele in allele_list:
        gene = allele.split("*")[0]   # e.g. "A*02" → "A"
        sero = mapping.get(gene, {}).get(allele)
        sero_list.append(sero)

    return sero_list
