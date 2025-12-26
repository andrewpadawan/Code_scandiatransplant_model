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
from agents.organs import *
from collections import defaultdict
from utils.check_distributions import *
from patient_generators.generating_constants import hla_to_serologic
from patient_generators.generating_utils import build_serologic_to_genetic
from visualizer.heatmap import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta
from visualizer.plot_distributions import *
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import scipy
from scipy.stats import truncnorm
from utils.plot_dist import *
from patient_generators.generating_utils import *
#organ_flows= pd.read_csv(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\csv_logs")

#donor_generator.generate_donor(300, 1, 5, r"testing_files/advanced_donor.csv")
#recipient_generator.generate_recipient(1000, 1, 5, r"testing_files/advanced_recipient.csv")
#check_age_distribution_by_groups_donors("testing_files/intermediate_donor.csv")
#check_hla_distributions("testing_files/intermediate_donor.csv")
#check_dist= hs_distribution("testing_files/intermediate_recipient.csv")
#print(check_dist)
#print(build_serologic_to_genetic(hla_to_serologic))

#plot_transfer_heatmap(r'C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\logs\summary_logs\city_flows_matching_20251110_155753.csv')
#alpha, beta_params = fit_beta(0, 3, 80)
#print("Fitted alpha:", alpha, "beta:", beta_params)
#plot_trunc_normal_HS()

# Example fitted parameters (replace with your own)
#alpha_lower, beta_lower = 1.4892255106168255, 7.838299843126989   # for 0–0.8 range
#alpha_high, beta_high   = 5.089324508243971, 0.3206297252229449   # for 0.8–1 range

#plot_beta_dist_cPRA()
#summarize_cpra_by_status("testing_files/intermediate_recipient.csv")

#print(summarize_by_cPRA("testing_files/intermediate_recipient.csv"))

#plot_cPRA_histogram_percent_from_csv("testing_files/intermediate_recipient.csv")

# Load your CSV file
#df = pd.read_csv(r"testing_files/advanced_recipient.csv")

# Select the columns you want
#print(df[["ABO_BLOOD_GROUP", "cPRA", "TS"]])
"""
if (df["cPRA"] > 1).any(): 
    print("Warning: Some cPRA values exceed 1")
else:
    print("Bug fixed")


"""



df = pd.read_csv(r"logs/csv_logs/matching_20251226_205635.csv")

check_priority_groups(df).to_csv("priority_summary.csv")