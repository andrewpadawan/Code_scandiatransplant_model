import random
import pandas as pd
from patient_generators.generating_utils import generate_blood_types
from patient_generators.generating_utils import generate_locations, generate_timesteps
from patient_generators.generating_constants import abo_dist, rh_dist


def generate_donor(total_samples, min_timestep, max_timestep, output_filepath):
    abo, rh = generate_blood_types(abo_dist, rh_dist, total_samples)
    city_list, country_list = generate_locations(total_samples)
    donor_ids= []


    for i in range(len(abo)):
        donor_ids.append("D" + str(i).zfill(4))

    # Make my pandas df
    headers = ['DONORNUMBER', 'AB0_BLOOD_GROUP', 'RHESUS_CODE', 'GRAFT_TYPE', "CITY", "COUNTRY", "TIMESTEP_ENTERED", 'Notes']
    df = pd.DataFrame(columns=headers)

    
    
    df["DONORNUMBER"]= donor_ids
    df["AB0_BLOOD_GROUP"]= abo
    df["RHESUS_CODE"] = rh
    #For now all organs are kidneys. The proper way KD: Double Kidney;KL: Left Kidney;KR: Right
    df["GRAFT_TYPE"]= "KD"
    df["CITY"]= city_list
    df["COUNTRY"]= country_list
    df["TIMESTEP_ENTERED"]= generate_timesteps(total_samples, 0, min_timestep, max_timestep)
    # Preview
    print("Generated " + str(total_samples) +  " donors between timesteps " + str(min_timestep) + " and " + str(max_timestep) )
    df.to_csv(output_filepath, index=False)

    




