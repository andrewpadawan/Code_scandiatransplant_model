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



#organ_flows= pd.read_csv(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\csv_logs")

#donor_generator.generate_donor(631, 1, 365, r"testing_files/basic_donor.csv")
#recipient_generator.generate_recipient(3367, 1, 365, r"testing_files/basic_recipient.csv")
match_file= r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\logs\csv_logs\matching_20251105_161721.csv"
#animate_organ_flows(csv_path=match_file, shapefile_path=r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\book_keeping\ne_110m_admin_0_countries\ne_110m_admin_0_countries.shp")
summarize_organ_flows(csv_path=match_file)
plot_organ_flow_graph_on_map(csv_path=match_file)
#plot_organ_flow_graph_on_map(csv_path=match_file)
