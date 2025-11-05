import pandas as pd
from utils.logger import get_matching_logger, log_match, log_match_csv_dynamic

logger = get_matching_logger()
has_logged_matching = False

def matching(scandiatransplant, timestep,log_timestamp, heuristic="greedy", verbose=True,  **kwargs):
    global has_logged_matching

    if not has_logged_matching:
        logger.info(f"Running matching with heuristic: {heuristic}")
        has_logged_matching = True
    

    if verbose:
        print(f"Running matching with heuristic: {heuristic}")

    if heuristic == "greedy":
        scandiatransplant, log_path= _greedy_match(scandiatransplant,timestep, log_timestamp, verbose=verbose, **kwargs)
    #elif heuristic == "priority":
        #_priority_match(scandiatransplant, verbose=verbose, **kwargs)
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
