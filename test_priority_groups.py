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
from utils.scenario_loader import load_organs
#organ_flows= pd.read_csv(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\csv_logs")

#donor_generator.generate_donor(1, 1, 5, r"testing_files/test_priority_donor.csv")
#recipient_generator.generate_recipient(5, 1, 1, r"testing_files/test_priority_recipient.csv")

donor= pd.read_csv(r"testing_files/test_priority_donor.csv")
recipient_df= pd.read_csv( r"testing_files/test_priority_7_recipient.csv")

organs= load_organs(donor)
my_organ= organs[0]


print(cascading_priority_allocation( recipient_df,my_organ, 1, True))