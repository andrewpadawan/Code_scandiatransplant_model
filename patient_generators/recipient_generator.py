
import pandas as pd
from patient_generators.generating_utils import generate_blood_types
from patient_generators.generating_utils import generate_locations
from patient_generators.generating_utils import generate_timesteps
from patient_generators.generating_constants import abo_dist, rh_dist


def generate_recipient(total_samples, min_timestep, max_timestep, output_filepath):
    
    abo, rh = generate_blood_types(abo_dist, rh_dist, total_samples)
    city_list, country_list = generate_locations(total_samples)
    recipient_ids= []

    # Make my pandas df
    headers = ['RECIPIENTNUMBER', 'AB0_BLOOD_GROUP', 'RHESUS_CODE', 'ORGAN',"CITY", "COUNTRY","TIMESTEP_ENTERED", 'Notes']
    df = pd.DataFrame(columns=headers)

    for i in range(len(abo)):
        recipient_ids.append("R" + str(i).zfill(4))
    
    df["RECIPIENTNUMBER"]= recipient_ids
    df["AB0_BLOOD_GROUP"]= abo
    df["RHESUS_CODE"] = rh
    #For now all organs are kidneys. The proper way KD: Double Kidney;KL: Left Kidney;KR: Right
    df["ORGAN"]= "Kidney"
    df["CITY"]= city_list
    df["COUNTRY"]= country_list
    df["TIMESTEP_ENTERED"]= generate_timesteps(total_samples, 0.6, min_timestep, max_timestep)
    
    print("Generated " + str(total_samples) +  " recipients between timesteps " + str(min_timestep) + " and " + str(max_timestep) )
    # Preview
    df.to_csv(output_filepath, index=False)



