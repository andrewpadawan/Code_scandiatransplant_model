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
from visualizer.summary import summarize_organ_flows
from visualizer.graphs import plot_organ_flow_graph_on_map
from datetime import datetime

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

logger = get_matching_logger()
#donor_generator.generate_donor(10, 1, 10)
#recipient_generator.generate_recipient(40, 1, 10)

# LOAD SCENARIOS
scandiatransplant, hospitals_loaded, df_ALL_recipients, df_ALL_donors= scenario_loader.load_scenario(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\scenarios\basic_scenario.json")


#for country in scandiatransplant.member_countries:
#    country.print()
#print(scandiatransplant.recipient_waitlist.df)

# Group both DataFrames by TIMESTEP
recipient_groups = df_ALL_recipients.groupby("TIMESTEP_ENTERED")
donor_groups = df_ALL_donors.groupby("TIMESTEP_ENTERED")

# Get all unique timesteps from both groups
all_timesteps = sorted(set(recipient_groups.groups.keys()) | set(donor_groups.groups.keys()))

timesteps_to_process = [t for t in all_timesteps if t > 0]

match_file= None
log_timestamp= datetime.now().strftime("%Y%m%d_%H%M%S")

# Loop through timesteps starting from 1
for t in timesteps_to_process:
    log_timestep(logger, t)
    #print("TIMESTEP " + str(t)+ " ____________________________")
    recipients_at_t = recipient_groups.get_group(t) if t in recipient_groups.groups else pd.DataFrame()
    donors_at_t = donor_groups.get_group(t) if t in donor_groups.groups else pd.DataFrame()
    
    #add to scandiatranplant waitlist
    # Skip empty timesteps
    if recipients_at_t.empty and donors_at_t.empty:
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

    #print("Before matching")
    #print(scandiatransplant.donor_list.df)


    scandiatransplant, incoming_match_file= matching(scandiatransplant,t, log_timestamp,"greedy", False)
    if incoming_match_file is not None:
        match_file= incoming_match_file
    
    #print("After matching")
    #print(scandiatransplant.donor_list.df)
    

print(str(match_file))
#print(scandiatransplant.recipient_waitlist.df)
#print(scandiatransplant.donor_list.df)


animate_organ_flows(csv_path=match_file, shapefile_path=r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\book_keeping\ne_110m_admin_0_countries\ne_110m_admin_0_countries.shp")
summarize_organ_flows(csv_path=match_file)
plot_organ_flow_graph_on_map(csv_path=match_file)
