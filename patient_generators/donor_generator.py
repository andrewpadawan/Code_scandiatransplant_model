import random
import pandas as pd
from patient_generators.generating_utils import generate_blood_types
from patient_generators.generating_utils import generate_locations
from book_keeping.locations import city_pop



abo_dist = {'O': 41, 'A': 44, 'B': 11, 'AB': 4}
rh_dist = {'POS': 85, 'NEG': 15}



def generate_donor(total_samples):
    abo, rh = generate_blood_types(abo_dist, rh_dist, total_samples)
    donor_ids= []


    for i in range(len(abo)):
        donor_ids.append("D"+ str(i))

    # Make my pandas df
    headers = ['DONORNUMBER', 'AB0_BLOOD_GROUP', 'RHESUS_CODE', 'GRAFT_TYPE', "CITY", "COUNTRY", 'Notes']
    df = pd.DataFrame(columns=headers)

    
    
    df["DONORNUMBER"]= donor_ids
    df["AB0_BLOOD_GROUP"]= abo
    df["RHESUS_CODE"] = rh
    #For now all organs are kidneys. The proper way KD: Double Kidney;KL: Left Kidney;KR: Right
    df["GRAFT_TYPE"]= "KD"


    # Preview
    df.to_csv('testing_files/basic_donor.csv', index=False)

    print(generate_locations(50))




