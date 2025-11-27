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
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import scipy
from scipy.stats import truncnorm
from utils.plot_dist import *

#organ_flows= pd.read_csv(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\csv_logs")

#donor_generator.generate_donor(100, 1, 5, r"testing_files/intermediate_donor.csv")
recipient_generator.generate_recipient(10000, 1, 5, r"testing_files/intermediate_recipient.csv")
#check_age_distribution_by_groups_donors("testing_files/intermediate_donor.csv")
#check_hla_distributions("testing_files/intermediate_donor.csv")
#check_dist= hs_distribution("testing_files/intermediate_recipient.csv")
#print(check_dist)
#print(build_serologic_to_genetic(hla_to_serologic))
summarize_cpra_by_status("testing_files/intermediate_recipient.csv")
#alpha, beta_params = fit_beta(0, 3, 80)
#print("Fitted alpha:", alpha, "beta:", beta_params)
#plot_trunc_normal_HS()