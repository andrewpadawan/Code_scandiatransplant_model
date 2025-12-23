import pandas as pd
from utils.logger import get_matching_logger, log_match, log_match_csv_dynamic
from agents.organs import *
from typing import List
from agents.hospital import *
from matching.match_utils import *
from matching.priority_ordering import *
from matching.priority_grouping import *

def local_cascading_priority_allocation(recipient_df, organ, timestep, verbose):
#This function reuses the priority groups and orderings from Scandiatransplant, but applies them to the local waiting list
#If no match is found on the local waiting list, the national waiting list is found. This is handled by the function that calls this one.
#If still no match, surplus
    #LAMP
    LAMP= check_priority_6(recipient_df, organ, verbose)
    if not LAMP.empty:
        ordered_LAMP= ordering_priority_2_to_7(LAMP, organ,timestep,verbose)
        print("LAMP")
        return ordered_LAMP
   
    priority_2= check_priority_2(recipient_df, organ, verbose)
    if not priority_2.empty:
        ordered_priority_2= ordering_priority_2_to_7(priority_2,organ, timestep,verbose)
        print("Priority 2")
        return ordered_priority_2
    
    priority_3= check_priority_3(recipient_df, organ, verbose)
    if not priority_3.empty:
        ordered_priority_3= ordering_priority_2_to_7(priority_3,organ, timestep, verbose)
        print("Priority 3")
        return ordered_priority_3
    
    priority_4= check_priority_4(recipient_df, organ, verbose)
    if not priority_4.empty:
        ordered_priority_4= ordering_priority_2_to_7(priority_4,organ, timestep,verbose)
        print("Priority 4")
        return ordered_priority_4
    
    priority_5= check_priority_5(recipient_df, organ, verbose)
    if not priority_5.empty:
        ordered_priority_5= ordering_priority_2_to_7(priority_5,organ, timestep,verbose)
        print("Priority 5")
        return ordered_priority_5
    #No payback because its local

    priority_7= check_priority_7(recipient_df, organ, verbose)
    if not priority_7.empty:
        ordered_priority_7= ordering_priority_2_to_7(priority_7,organ,timestep,verbose)
        print("Priority 7")
        return ordered_priority_7
    
    #surplus organs handled by the function that calls this one

    #if no priority groups found, return empty dataframe
    return recipient_df[0:0]
