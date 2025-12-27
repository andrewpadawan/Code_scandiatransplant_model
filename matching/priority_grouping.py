import pandas as pd
from utils.logger import get_matching_logger, log_match, log_match_csv_dynamic
from agents.organs import *
from typing import List
from agents.hospital import *
from matching.match_utils import *
from matching.priority_ordering import *
from matching.priority_enum import *
import copy


def cascading_priority_allocation(recipient_df, organ, timestep,scandiatransplant, verbose):
    print(f"Allocating organ {organ.organ_id} at Scandiatransplant level")
    priority_1= check_priority_1(recipient_df, organ, verbose)
    if not priority_1.empty:
        ordered_priority_1= ordering_priority_1(priority_1,organ, timestep,verbose )
        print("Priority 1")
        return ordered_priority_1, AllocationPriority.PRIORITY_1
    
    priority_2= check_priority_2(recipient_df, organ, verbose)
    if not priority_2.empty:
        ordered_priority_2= ordering_priority_2_to_7(priority_2,organ, timestep,verbose)
        print("Priority 2")
        return ordered_priority_2, AllocationPriority.PRIORITY_2
    
    priority_3= check_priority_3(recipient_df, organ, verbose)
    if not priority_3.empty:
        ordered_priority_3= ordering_priority_2_to_7(priority_3,organ, timestep, verbose)
        print("Priority 3")
        return ordered_priority_3, AllocationPriority.PRIORITY_3
    
    priority_4= check_priority_4(recipient_df, organ, verbose)
    if not priority_4.empty:
        ordered_priority_4= ordering_priority_2_to_7(priority_4,organ, timestep,verbose)
        print("Priority 4")
        return ordered_priority_4, AllocationPriority.PRIORITY_4
    
    priority_5= check_priority_5(recipient_df, organ, verbose)
    if not priority_5.empty:
        ordered_priority_5= ordering_priority_2_to_7(priority_5,organ, timestep,verbose)
        print("Priority 5")
        return ordered_priority_5, AllocationPriority.PRIORITY_5
    #TODO payback rules here
    priority_6= check_priority_6(recipient_df, organ, verbose)
    if not priority_6.empty:
        ordered_priority_6= ordering_priority_2_to_7(priority_6, organ,timestep,verbose)
        print("Priority 6")
        return ordered_priority_6, AllocationPriority.PRIORITY_6
    priority_7= check_priority_7(recipient_df, organ, verbose)
    if not priority_7.empty:
        ordered_priority_7= ordering_priority_2_to_7(priority_7,organ,timestep,verbose)
        print("Priority 7")
        return ordered_priority_7, AllocationPriority.PRIORITY_7
    
    matched_recipient_df, priority_level_assigned= handle_surplus_organs(recipient_df, organ, timestep, scandiatransplant, True)
    return matched_recipient_df, priority_level_assigned
    #if no priority groups found, return empty dataframe
    #return recipient_df[0:0]

# ...........................................................
def local_cascading_priority_allocation(recipient_df, organ, timestep, verbose= False):
#This function reuses the priority groups and orderings from Scandiatransplant, but applies them to the local waiting list
#If no match is found on the local waiting list, the national waiting list is found. This is handled by the function that calls this one.
#If still no match, surplus
    #LAMP
    print(f"Allocating organ {organ.organ_id} at local level")

    LAMP= check_priority_6(recipient_df, organ, verbose)
    if not LAMP.empty:
        ordered_LAMP= ordering_priority_2_to_7(LAMP, organ,timestep,verbose)
        print("LAMP")
        return ordered_LAMP, AllocationPriority.LOCAL
   
    priority_2= check_priority_2(recipient_df, organ, verbose)
    if not priority_2.empty:
        ordered_priority_2= ordering_priority_2_to_7(priority_2,organ, timestep,verbose)
        print("Priority 2")
        return ordered_priority_2, AllocationPriority.LOCAL
    
    priority_3= check_priority_3(recipient_df, organ, verbose)
    if not priority_3.empty:
        ordered_priority_3= ordering_priority_2_to_7(priority_3,organ, timestep, verbose)
        print("Priority 3")
        return ordered_priority_3, AllocationPriority.LOCAL
    
    priority_4= check_priority_4(recipient_df, organ, verbose)
    if not priority_4.empty:
        ordered_priority_4= ordering_priority_2_to_7(priority_4,organ, timestep,verbose)
        print("Priority 4")
        return ordered_priority_4, AllocationPriority.LOCAL
    
    priority_5= check_priority_5(recipient_df, organ, verbose)
    if not priority_5.empty:
        ordered_priority_5= ordering_priority_2_to_7(priority_5,organ, timestep,verbose)
        print("Priority 5")
        return ordered_priority_5, AllocationPriority.LOCAL
    #No payback because its local

    priority_7= check_priority_7(recipient_df, organ, verbose)
    if not priority_7.empty:
        ordered_priority_7= ordering_priority_2_to_7(priority_7,organ,timestep,verbose)
        print("Priority 7")
        return ordered_priority_7, AllocationPriority.LOCAL
    
    #surplus organs handled by the function that calls this one

    #if no priority groups found, return empty dataframe
    return recipient_df[0:0], AllocationPriority.NONE

#...................................................................

def handle_surplus_organs(recipient_df, organ, timestep, scandiatransplant, verbose):
    print("Handling surplus organ")
    
    offering_center= organ.city
    rota_list = scandiatransplant.rota

    same_country = [h for h in scandiatransplant.rota 
                if h.country == organ.country and h.city != offering_center]

    other_countries = [h for h in scandiatransplant.rota 
                   if h.country != organ.country]

    #Organs are first offered to centers in the same country and then the rest
    #This puts the centers in rota order in both categories, one after the other.
    for hospital in same_country + other_countries:
        #see fif there is a match inside that hospital: this is the criteria for accepting
        #the first hospital in the rota that has a match gets the organ
        # Skip the offering center 


        new_organ = copy.deepcopy(organ) 
        new_organ.city = hospital.city
        matched_recipient_df, priority_level_assigned= local_cascading_priority_allocation(recipient_df, new_organ, timestep, verbose)
        if verbose:
                print(f"Organ offered by {offering_center} to {hospital.city}")
        
        
        if not matched_recipient_df.empty:
            if verbose:
                print(f"Organ given by {offering_center} to {hospital.city}")    # Make a deep copy of the organ 

            scandiatransplant.remove_organ_by_id(organ.organ_id)
            #Update rota list
            # Move the chosen hospital to the end of the rota
            scandiatransplant.rota.remove(hospital)
            scandiatransplant.rota.append(hospital)

            return matched_recipient_df, AllocationPriority.SURPLUS
        

    if verbose: print(f"No matched recipient for surplus organ {organ.organ_id} at timestep {timestep}") 
    # Return an empty DataFrame and AllocationPriority.NONE 
        
    return recipient_df[0:0], AllocationPriority.NONE



    
    

def check_priority_1(recipient_df, organ, verbose):
    if verbose:
        print("For priority 1")
    #Patient with STAMP-status that are ABO compatible with donor and where all donor HLA-A, 
    #B, -C -DRB1, -DRB3/4/5, -DQA1, -DQB1, -DPA1, -DPB1 antigens are either shared with the 
    #recipient or are among those defined as acceptable.
    valid_indices = []
    for idx, recipient_row in recipient_df.iterrows():
        if not check_STAMP_status(recipient_row):
            continue
        elif not is_ABO_compatible(recipient_row, organ):
            continue
        
        # Wrap row into one-row DataFrame for compatibility filter
        recipient_one_df = recipient_row.to_frame().T
        compatible_df = filter_ALL_HLA_compatible(organ, recipient_one_df)
        if compatible_df .empty:
            continue
        
        valid_indices.append(idx)
    
    # Slice the original DataFrame to return only the valid recipients
    return recipient_df.loc[valid_indices]
    


def check_priority_2(recipient_df, organ, verbose):
    if verbose:
        print("For priority 2")
    #Highly immunized (PRA ≥ 80%) patients who are HLA-A, -B, -DRB1 compatible with donor. 
    valid_indices = []
    abo_identical_df= abo_identical_priority_2_to_5(recipient_df, organ)

        

    for idx, recipient_row in abo_identical_df.iterrows():
        cpra = recipient_row["cPRA"]
        if cpra < 0.80:  # must be ≥ 80%
            continue
        if verbose:
            print("cPRA check passed by "+ str(idx))
        # Wrap row into one-row DataFrame for compatibility filter
        recipient_one_df = recipient_row.to_frame().T
        compatible_df = filter_HLA_A_B_DRB1_compatible(organ, recipient_one_df)

        if compatible_df.empty:
            continue

        valid_indices.append(idx)

    # Return a DataFrame of all valid recipients
    return recipient_df.loc[valid_indices]



def check_priority_3(recipient_df, organ, verbose):
    if verbose:
        print("For priority 3")
    #Immunized patients (PRA ≥ 10% but below 80%) who are HLA-A, -B, -DRB1 compatible with donor. 
    valid_indices = []
    abo_identical_df= abo_identical_priority_2_to_5(recipient_df, organ)

    for idx, recipient_row in abo_identical_df.iterrows():
        cpra = recipient_row["cPRA"]
        # PRA must be between 10% and 79%
        if cpra < 0.10 or cpra >= 0.80:
            continue

        # Wrap row into one-row DataFrame for compatibility filter
        recipient_one_df = recipient_row.to_frame().T
        compatible_df = filter_HLA_A_B_DRB1_compatible(organ, recipient_one_df)

        if compatible_df.empty:
            continue

        valid_indices.append(idx)

    # Return a DataFrame of all valid recipients
    return recipient_df.loc[valid_indices]


def check_priority_4(recipient_df, organ, verbose):
    if verbose:
        print("For priority 4")
    #If organ donor is <50 years of age, at least one kidney is offered to recipient <16 years of age 
    #(counted from time of registration), if there is HLA-DRB1 compatibility and in addition not 
    #more than 2 HLA-A, B mismatches. 
    #If donor is older than 50 this priority does not apply

    donor_age= organ.donor_age
    
    if donor_age > 50:
        return recipient_df.iloc[0:0]

    abo_identical_df= abo_identical_priority_2_to_5(recipient_df, organ)

    if not abo_identical_df.empty:
        under_16_hla_a_b_under_2_mismatch= filter_priority_4_compatible(organ, abo_identical_df, verbose)
    else:
        return recipient_df.iloc[0:0]
    # Return a DataFrame of all valid recipients
    return under_16_hla_a_b_under_2_mismatch


def check_priority_5(recipient_df, organ,verbose ):
    if verbose:
        print("For priority 5")
    valid_indices= []
    #Patients < 60 years of age who are HLA-A, -B, -DRB1 compatible with donor unless the proposed recipient is > 30 years older than the donor 
    #For patients under the age of 60
    under_60= recipient_df[recipient_df["AGE"] < 60]
    if under_60.empty:
        return recipient_df.iloc[0:0]
    abo_identical_df= abo_identical_priority_2_to_5(under_60, organ)

    for idx, recipient_row in abo_identical_df.iterrows():
        age_donor= organ.donor_age
        age_recipient= recipient_row["AGE"]

        #If proposed recipient is more than 30 years older than the donor, skip
        if age_recipient - age_donor>30:
            continue

        # Wrap row into one-row DataFrame for compatibility filter
        recipient_one_df = recipient_row.to_frame().T
        compatible_df = filter_HLA_A_B_DRB1_compatible(organ, recipient_one_df)

        if compatible_df.empty:
            continue

        valid_indices.append(idx)

    # Return a DataFrame of all valid recipients
    return recipient_df.loc[valid_indices]


def check_priority_6(recipient_df, organ, verbose):
    if verbose:
        print("For priority 6")
    #Priority 6 corresponds to LAMP status, local version of STAMP
    #This program is a local version of STAMP. At recipient search the patients are matched 
    #the same way as STAMP patients, due to defined acceptable mismatches. The program 
    #does not result in any exchange obligations between centers.
    #The critri afor acceptance s depending on each center, scandiatransplant does not oversee. i will use cpra bigger or equal to 80%
    
    #Uses the local list
    organ_location= organ.city
    local_recipient_df = recipient_df[recipient_df["CITY"] == organ_location]

    valid_indices = []

    for idx, recipient_row in local_recipient_df.iterrows():
        if not recipient_row["cPRA"] >= 0.80:
            continue
        elif not is_ABO_compatible(recipient_row, organ):
            continue
        
        # Wrap row into one-row DataFrame for compatibility filter
        recipient_one_df = recipient_row.to_frame().T
        compatible_df = filter_ALL_HLA_compatible(organ, recipient_one_df)
        if compatible_df .empty:
            continue
        
        valid_indices.append(idx)
    
    # Slice the original DataFrame to return only the valid recipients
    return recipient_df.loc[valid_indices]


def check_priority_7(recipient_df, organ, verbose):
    if verbose:
        print("For priority 7")
# THIS IS ONE THE PROCUREMENTE CENTER'S OWN WAITING LIST
    organ_location= organ.city
    local_recipient_df = recipient_df[recipient_df["CITY"] == organ_location]

    valid_indices = []
    for idx, recipient_row in local_recipient_df.iterrows():
        if not is_ABO_compatible(recipient_row, organ):
            continue
        
        # Wrap row into one-row DataFrame for compatibility filter
        recipient_one_df = recipient_row.to_frame().T
        compatible_df = filter_ALL_HLA_compatible(organ, recipient_one_df)
        if compatible_df.empty:
            continue
        
        valid_indices.append(idx)
    
    # Slice the original DataFrame to return only the valid recipients
    return recipient_df.loc[valid_indices]
