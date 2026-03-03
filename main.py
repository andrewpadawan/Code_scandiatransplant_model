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
logger = get_matching_logger()


print("Initialize matching module")
# LOAD SCENARIOS
scandiatransplant, hospitals_loaded, df_ALL_recipients, df_ALL_donors, organ_list= scenario_loader.load_scenario(r"scenarios\advanced_scenario.json")


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
    print("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
    print("In timestep:" + str(t))
    
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
    #scandiatransplant, incoming_match_file= matching(scandiatransplant,t, log_timestamp,organs_at_t,True,"sctp", False)

    #Match the Scandiatransplant waiting list

    scandiatransplant, incoming_match_file= matching(scandiatransplant,t, log_timestamp,organs_at_t,False,"sctp", False)
    

    if incoming_match_file is not None:
        match_file= incoming_match_file
    



#animate_organ_flows(csv_path=match_file, shapefile_path=r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\book_keeping\ne_110m_admin_0_countries\ne_110m_admin_0_countries.shp")

#plot_organ_flow_graph_on_map(csv_path=match_file)
for hospital in Hospital.registry:
    print(f"=== Exchange table for {hospital.city} ===")
    print(hospital.organ_exchange_table.to_string(col_space=12))
    print()


df = pd.read_csv(match_file)

check_priority_groups(df).to_csv("priority_summary.csv")

summarize_organ_flows_countries(csv_path=match_file)
calculate_implementation_stats(csv_path=match_file)
summary_file= get_summary_file(match_file)
#print(summary_file)
plot_transfer_heatmap(summary_file)

