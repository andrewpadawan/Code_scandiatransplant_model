import book_keeping
from patient_generators import *
from patient_generators import generating_utils
from utils import scenario_loader
import sys
import os
import pandas as pd 

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


#donor_generator.generate_donor(20)
#recipient_generator.generate_recipient(20)

# LOAD SCENARIOS
scandiatransplant, hospitals_loaded, df_ALL_recipients, df_ALL_donors= scenario_loader.load_scenario(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\scenarios\basic_scenario.json")
print(scandiatransplant.donor_list.df)

#for country in scandiatransplant.member_countries:
#    country.print()
#print(scandiatransplant.recipient_waitlist.df)

# Group both DataFrames by TIMESTEP
recipient_groups = df_ALL_recipients.groupby("TIMESTEP_ENTERED")
donor_groups = df_ALL_donors.groupby("TIMESTEP_ENTERED")

# Get all unique timesteps from both groups
all_timesteps = sorted(set(recipient_groups.groups.keys()) | set(donor_groups.groups.keys()))

timesteps_to_process = [t for t in all_timesteps if t > 0]

# Loop through timesteps starting from 1
for t in timesteps_to_process:
    print("TIMESTEP " + str(t)+ " ____________________________")
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

scandiatransplant.recipient_waitlist.sort("TIMESTEP_ENTERED")
scandiatransplant.donor_list.sort("TIMESTEP_ENTERED")