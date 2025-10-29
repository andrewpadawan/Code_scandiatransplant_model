import book_keeping
from patient_generators import *
from patient_generators import generating_utils
from utils import scenario_loader
import sys
import os
import pandas as pd 
from matching.match_donor_patient import *
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

scandiatransplant, hospitals_loaded, df_ALL_recipients, df_ALL_donors= scenario_loader.load_scenario(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\scenarios\basic_scenario.json")

print(df_ALL_donors)
recipient_groups = df_ALL_recipients.groupby("TIMESTEP_ENTERED")
donor_groups = df_ALL_donors.groupby("TIMESTEP_ENTERED")
print(donor_groups.get_group(7) if 7 in donor_groups.groups else "None found")

all_timesteps = sorted(set(recipient_groups.groups.keys()) | set(donor_groups.groups.keys()))
print(all_timesteps)