import book_keeping
from patient_generators import *
from patient_generators import generating_utils
from utils import scenario_loader
from utils.logger import log_timestep
import os
import pandas as pd 
from matching.match_donor_patient import *
import sys
from visualizer.organ_flow_visualizer import animate_organ_flows
from visualizer.summary import *
from visualizer.graphs import plot_organ_flow_graph_on_map
from datetime import datetime
from collections import defaultdict
from agents.hospital import *
from visualizer.heatmap import *
from utils.aux_functions import *
from visualizer.implementation_stats import *

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils.check_distributions import *


def run_Scandiatransplant_model(w_mismatch,w_distance, w_payback):



    logger = get_matching_logger()





    #donor_generator.generate_donor(10, 1, 10)
    #recipient_generator.generate_recipient(40, 1, 10)

    print("Initialize simulation module")
    # LOAD SCENARIOS
    #scandiatransplant, hospitals_loaded, df_ALL_recipients, df_ALL_donors, organ_list= scenario_loader.load_scenario(r"C:\Users\reddr\Documents\Scandiatransplant_modelling\scenarios\opt_metaheuristics.json")
    scandiatransplant, hospitals_loaded, df_ALL_recipients, df_ALL_donors, organ_list= scenario_loader.load_scenario(r"scenarios\advanced_scenario.json")



    #for country in scandiatransplant.member_countries:
    #    country.print()
    #print(scandiatransplant.recipient_waitlist.df)

    # Group both DataFrames by TIMESTEP
    recipient_groups = df_ALL_recipients.groupby("TIMESTEP_ENTERED")
    donor_groups = df_ALL_donors.groupby("TIMESTEP_ENTERED")
    organ_groups= defaultdict(list)
    for organ in organ_list:
        organ_groups[organ.timestep].append(organ)


    # Get all unique timesteps from both groups
    all_timesteps = sorted(set(recipient_groups.groups.keys()) | set(donor_groups.groups.keys()))

    timesteps_to_process = [t for t in all_timesteps if t > 0]

    match_file= None
    log_timestamp= datetime.now().strftime("%Y%m%d_%H%M%S")

    # Loop through timesteps starting from 1
    for t in timesteps_to_process:
        
        #print("In timestep:" + str(t))
        
        log_timestep(logger, t)
        #print("TIMESTEP " + str(t)+ " ____________________________")
        recipients_at_t = recipient_groups.get_group(t) if t in recipient_groups.groups else pd.DataFrame()
        donors_at_t = donor_groups.get_group(t) if t in donor_groups.groups else pd.DataFrame()
        organs_at_t = organ_groups.get(t, [])

        
        #add to scandiatranplant waitlist
        # Skip empty timesteps
        if recipients_at_t.empty and len(organs_at_t) == 0:
            continue

        # Add recipients to waitlist
        for _, row in recipients_at_t.iterrows():
            patient_row_df = pd.DataFrame([row])
            #print(patient_row_df)
            scandiatransplant.add_recipient(patient_row_df)

        # Add donors to donor list
        for _, row in donors_at_t.iterrows():
            donor_row_df = pd.DataFrame([row])
            scandiatransplant.add_donor(donor_row_df)

        scandiatransplant.organ_list.extend(organs_at_t)

        #scandiatransplant.print()
        #Match the local waiting list
        scandiatransplant, incoming_match_file= matching(scandiatransplant,t, log_timestamp,organs_at_t,True,w_mismatch, w_distance,w_payback,"sctp", False)

        #Match the Scandiatransplant waiting list

        scandiatransplant, incoming_match_file= matching(scandiatransplant,t, log_timestamp,organs_at_t,False,w_mismatch, w_distance,w_payback,"sctp", False)
        

        #for hospital in Hospital.registry:
        #    hospital.print()



        if incoming_match_file is not None:
            match_file= incoming_match_file
        

        #print("After matching")
        #print(scandiatransplant.donor_list.df)
        

    #print(str(match_file))
    #print(scandiatransplant.recipient_waitlist.df)
    #print(scandiatransplant.donor_list.df)


    #animate_organ_flows(csv_path=match_file, shapefile_path=r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\book_keeping\ne_110m_admin_0_countries\ne_110m_admin_0_countries.shp")

    #plot_organ_flow_graph_on_map(csv_path=match_file)


    df = pd.read_csv(match_file)

    #check_priority_groups(df).to_csv("priority_summary.csv")

    summarize_organ_flows_countries(csv_path=match_file)
    number_matches, total_distance_travelled_incl_local, total_mismatches, average_equity_coefficient= calculate_implementation_stats(csv_path=match_file)
    #summary_file= get_summary_file(match_file)
    #print(summary_file)
    #plot_transfer_heatmap(summary_file)
    
    print("Finished simulation module")
    return number_matches, total_distance_travelled_incl_local, total_mismatches, average_equity_coefficient



run_Scandiatransplant_model(200.24192977416442, 409.1681514455609, 1)
run_Scandiatransplant_model(297.26433233081787, 608.2010386816108, 1)
run_Scandiatransplant_model(465.34719864343555, 922.2968927727939, 1)
run_Scandiatransplant_model(340.4205940602128, 674.6314506164276, 1)
run_Scandiatransplant_model(105.44134495180398, 205.86913061351007, 1)
run_Scandiatransplant_model(349.43264790342255, 713.0716675547825, 1)
run_Scandiatransplant_model(285.606178623826, 571.9851426138772, 1)
run_Scandiatransplant_model(370.9625770302941, 739.6375381660981, 1)
run_Scandiatransplant_model(128.78253434620547, 232.0267656745305, 1)
run_Scandiatransplant_model(491.43446599669494, 974.8076237401524, 1)
run_Scandiatransplant_model(49.50344263524885, 95.00758418616051, 1)
run_Scandiatransplant_model(82.5044451036727, 163.82961508152675, 1)
run_Scandiatransplant_model(78.2104557354295, 129.8527464120167, 1)
run_Scandiatransplant_model(82.5044451036727, 163.82961508152675, 1)
run_Scandiatransplant_model(503.9650814502086, 1.8344893848013522, 1)
run_Scandiatransplant_model(103.78141809812125, 208.80596075445706, 1)
run_Scandiatransplant_model(268.273589031753, 541.1221522773317, 1)
run_Scandiatransplant_model(758.6396198711446, 419.9215918846899, 1)
run_Scandiatransplant_model(118.86976595912397, 236.4113097770033, 1)
run_Scandiatransplant_model(27.825233125429886, 56.08475738950128, 1)
run_Scandiatransplant_model(223.58484371739846, 141.15032931390041, 1)
