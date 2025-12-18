import pandas as pd
from utils.logger import get_matching_logger, log_match, log_match_csv_dynamic
from agents.organs import *
from typing import List
from agents.hospital import *
from matching.priority_grouping import *
#ABO compatibility, key is the donor, values the recipients

logger = get_matching_logger()
has_logged_matching = False

def matching(scandiatransplant, timestep,log_timestamp,organs_at_t,local, heuristic="greedy", verbose=True,  **kwargs):
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
    elif heuristic == "sctp":
        scandiatransplant, log_path=_sctp(scandiatransplant,timestep, log_timestamp,organs_at_t, verbose=verbose, **kwargs)
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
        
        HLA_compatible_recipient_df= filter_ALL_HLA_compatible(organ, recipient_df)
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



def _sctp(scandiatransplant,timestep, log_timestamp, organs_at_t: List[Organ],local,verbose=True,  **kwargs):
    if local:
        print()
        #Call the local allocation function here
        local_scandiatransplant_allocation(scandiatransplant,timestep, log_timestamp, organs_at_t,verbose=True)
    else:
        sctp_scandiatransplant_allocation(scandiatransplant,timestep, log_timestamp, organs_at_t,verbose=True)
    

#TODO pass recipient_row as df
#TODO add payback rules
#TODO log matches, log which priority group was used

def sctp_scandiatransplant_allocation(scandiatransplant,timestep, log_timestamp, organs_at_t: List[Organ], verbose=True,  **kwargs):
   
    if verbose:
        print("Using abo_Rh_match matching")
    
    donor_df_list= []
    recipient_df = None
    

    if scandiatransplant.donor_list.df.empty:
        if verbose:
            print("No donor was available at this timestep")
        return scandiatransplant, None
    
    if not scandiatransplant.recipient_waitlist.df.empty: #change for local lists
        recipient_df= scandiatransplant.recipient_waitlist.df.copy()
    else:
        if verbose:
            print("Recipient list was empty")
        return scandiatransplant, None


    for organ in organs_at_t:
        priority_df= cascading_priority_allocation(recipient_df, organ, timestep)


def local_scandiatransplant_allocation(scandiatransplant,timestep, log_timestamp, organs_at_t: List[Organ], verbose=True,  **kwargs):
    print()




# Auxiliary functions

