import pandas as pd
from utils.logger import get_matching_logger, log_match, log_match_csv_dynamic
from agents.organs import *
from typing import List
from agents.hospital import *
#ABO compatibility, key is the donor, values the recipients
abo_compatibility = {
    "O": ["O", "A", "B", "AB"],
    "A": ["A", "AB"],
    "B": ["B", "AB"],
    "AB": ["AB"]
}

logger = get_matching_logger()
has_logged_matching = False

def matching(scandiatransplant, timestep,log_timestamp,organs_at_t, heuristic="greedy", verbose=True,  **kwargs):
    global has_logged_matching

    if not has_logged_matching:
        logger.info(f"Running matching with heuristic: {heuristic}")
        has_logged_matching = True
    

    if verbose:
        print(f"Running matching with heuristic: {heuristic}")

    if heuristic == "greedy":
        scandiatransplant, log_path= _greedy_match(scandiatransplant,timestep, log_timestamp, verbose=verbose, **kwargs)
    elif heuristic == "abo_HLA_match":
        scandiatransplant, log_path=_abo_HLA_match(scandiatransplant,timestep, log_timestamp,organs_at_t, verbose=verbose, **kwargs)
    else:
        raise ValueError(f"Unknown heuristic: {heuristic}")
    
    return scandiatransplant, log_path

def _greedy_match(scandiatransplant, timestep, log_timestamp, verbose=True, **kwargs):
    if verbose:
        print("Using greedy matching")
    # Access scandiatransplant.recipient_waitlist, donor_list, etc.
    #1) sort thw waitlist by entry time
    scandiatransplant.recipient_waitlist.sort("TIMESTEP_ENTERED")
    scandiatransplant.donor_list.sort("TIMESTEP_ENTERED")
    #2) Assing a donor to 2 recipients
        #check if there are any available donors
    
    donor_df_list= []
    recipient_df = None
    recipient_index = 0

    if not scandiatransplant.donor_list.df.empty:
        donor_df_list= [scandiatransplant.donor_list.df.iloc[[i]] for i in range(len(scandiatransplant.donor_list.df))]
        #first_donor=  scandiatransplant.donor_list.df.head(1)
    else:
        if verbose:
            print("No donor was available at this timestep")
        return scandiatransplant, None
    
    if not scandiatransplant.recipient_waitlist.df.empty:
        recipient_df= scandiatransplant.recipient_waitlist.df.copy()
    else:
        if verbose:
            print("Recipient list was empty")
        return scandiatransplant, None
      
    #3) Print the match to a log file
    for donor in donor_df_list:
        if recipient_index + 2 > len(recipient_df):
            print("Not enough recipients left to match this donor.")
            break

        # Take two recipients without overlap
        recipient1_df = recipient_df.iloc[[recipient_index]]
        recipient2_df = recipient_df.iloc[[recipient_index + 1]]

        recipient_index += 2
    

        log_match(logger, donor, recipient1_df)
        log_match_csv_dynamic(timestep, donor, recipient1_df, log_timestamp)
        log_match(logger, donor, recipient2_df)
        log_path= log_match_csv_dynamic(timestep,donor, recipient2_df, log_timestamp)
        #4) Remove donor and recipients from scandiatransplant
        scandiatransplant.remove_donor(donor["DONORNUMBER"].values[0])
        scandiatransplant.remove_recipient(recipient1_df["RECIPIENTNUMBER"].values[0])
        scandiatransplant.remove_recipient(recipient2_df["RECIPIENTNUMBER"].values[0])



    return scandiatransplant, log_path if 'log_path' in locals() else None


def _abo_HLA_match(scandiatransplant,timestep, log_timestamp, organs_at_t: List[Organ], verbose=True,  **kwargs):
    #Very simple allocation policy:
    #1) If it matches (abo identical), check if payback, then sorted by time on waiting list
    #2) Abo compatible, check if payback, then sorted by time on waiting list
    #simple way of packback, just a counter
    
    if verbose:
        print("Using abo_Rh_match matching")
    
    donor_df_list= []
    recipient_df = None
    

    if scandiatransplant.donor_list.df.empty:
        #donor_df_list= [scandiatransplant.donor_list.df.iloc[[i]] for i in range(len(scandiatransplant.donor_list.df))]
        #donor_df= scandiatransplant.donor_list.df
        #first_donor=  scandiatransplant.donor_list.df.head(1)
        if verbose:
            print("No donor was available at this timestep")
        return scandiatransplant, None
    
    
    if not scandiatransplant.recipient_waitlist.df.empty:
        recipient_df= scandiatransplant.recipient_waitlist.df.copy()
    else:
        if verbose:
            print("Recipient list was empty")
        return scandiatransplant, None
      
    #3) Make and print the match to a log file
    for organ in organs_at_t:
        if not organ.exchange_obligation:
            continue
        if len(recipient_df) == 0:
            print("Not enough recipients left to match this organ.")
            break
        #make the match based on ABO Rh compatibility
        
        HLA_compatible_recipient_df= filter_HLA_compatible(organ, recipient_df)
        abo_identical_df = rank_abo_identical(organ, HLA_compatible_recipient_df)

        if not abo_identical_df.empty:
            recipient = abo_identical_df.iloc[[0]]
        else:
            abo_compatible_df = rank_abo_compatible(organ, HLA_compatible_recipient_df)
            
            if not abo_compatible_df.empty:
                recipient = abo_compatible_df.iloc[[0]]
            else:
                print("No match was found for this organ")
                continue

                  
    #log the matches
        log_match(logger, organ, recipient)
        log_path= log_match_csv_dynamic(timestep,organ, organ.donor_row, recipient, log_timestamp)
        #4) Remove donor and recipients from scandiatransplant
        scandiatransplant.remove_donor(organ.donor_id)
        scandiatransplant.remove_recipient(recipient["RECIPIENTNUMBER"].values[0])
        #log paybacks
        log_payback(recipient, organ)


    return scandiatransplant, log_path if 'log_path' in locals() else None



def filter_HLA_compatible(organ:Organ, recipient_df):
    donor_alleles = [
        organ.geno_HLA_A,
        organ.geno_HLA_B,
        organ.geno_HLA_C,
        organ.geno_HLA_DRB1,
        organ.geno_HLA_DQA1,
        organ.geno_HLA_DQB1,
        organ.geno_HLA_DPA1,
        organ.geno_HLA_DPB1,
    ]

    # Filter recipients: compatible if none of the donor alleles are in their antibody list
    compatible_df = recipient_df[
        ~recipient_df["HLA_antibodies"].apply(
            lambda ab_list: any(allele in ab_list for allele in donor_alleles)
        )
    ]
    
    return compatible_df

   

# Helping functions
def rank_abo_identical(organ:Organ, recipient_df):
    filtered_df = recipient_df[recipient_df["AB0_BLOOD_GROUP"] == organ.abo_blood]
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
        recipient_df["AB0_BLOOD_GROUP"].isin(compatible_types)
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