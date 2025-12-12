
import pandas as pd
from patient_generators.generating_utils import *

from patient_generators.generating_constants import *


def generate_recipient(total_samples, min_timestep, max_timestep, output_filepath):
    
    abo, rh = generate_blood_types(abo_dist, rh_dist, total_samples)
    city_list, country_list = generate_locations(total_samples)
    HS_no_yes_list= choose_HS_patients(total_samples)
    recipient_ids= []

    # Make my pandas df
    headers = ['RECIPIENTNUMBER', 'AB0_BLOOD_GROUP', 'RHESUS_CODE', 'ORGAN',"AGE","CITY", "COUNTRY","TIMESTEP_ENTERED","Genomic_HLA-A","Genomic_HLA-B","Genomic_HLA-C","Genomic_HLA-DRB1","Genomic_HLA-DQA1","Genomic_HLA-DQB1","Genomic_HLA-DPA1" ,"Genomic_HLA-DPB1","Serologic_HLA-A","Serologic_HLA-B","Serologic_HLA-C","Serologic_HLA-DRB1","Serologic_HLA-DQA1","Serologic_HLA-DQB1","Serologic_HLA-DPA1" ,"Serologic_HLA-DPB1",  "HLA_antibodies", "cPRA", "TS", 'Notes']
    df = pd.DataFrame(columns=headers)

    for i in range(len(abo)):
        recipient_ids.append("R" + str(i).zfill(4))
    
    df["RECIPIENTNUMBER"]= recipient_ids
    df["AB0_BLOOD_GROUP"]= abo
    df["RHESUS_CODE"] = rh
    #For now all organs are kidneys. The proper way KD: Double Kidney;KL: Left Kidney;KR: Right
    df["ORGAN"]= "Kidney"
    df["AGE"]= generate_recipient_ages(total_samples)
    df["CITY"]= city_list
    df["COUNTRY"]= country_list
    df["TIMESTEP_ENTERED"]= generate_timesteps(total_samples, 0.6, min_timestep, max_timestep)
    hla_genotype, hla_serology= generate_hla_genotypes(total_samples)
    
    
    df["Genomic_HLA-A"]= hla_genotype["A"]
    df["Genomic_HLA-B"]= hla_genotype["B"]
    df["Genomic_HLA-C"]= hla_genotype["C"]
    df["Genomic_HLA-DRB1"]= hla_genotype["DRB1"]
    df["Genomic_HLA-DQA1"]= hla_genotype["DQA1"]
    df["Genomic_HLA-DQB1"]= hla_genotype["DQB1"]
    df["Genomic_HLA-DPA1"]= hla_genotype["DPA1"]
    df["Genomic_HLA-DPB1"]= hla_genotype["DPB1"]
    df["Serologic_HLA-A"]= hla_serology["A"]
    df["Serologic_HLA-B"]= hla_serology["B"]
    df["Serologic_HLA-C"]= hla_serology["C"]
    df["Serologic_HLA-DRB1"]= hla_serology["DRB1"]
    df["Serologic_HLA-DQA1"]= hla_serology["DQA1"]
    df["Serologic_HLA-DQB1"]= hla_serology["DQB1"]
    df["Serologic_HLA-DPA1"]= hla_serology["DPA1"]
    df["Serologic_HLA-DPB1"]= hla_serology["DPB1"]
    #df["HS_status"]= HS_no_yes_list
    hla_antibodies_list, cpra_list, TS_list= generate_recipient_antibodies(total_samples,hla_serology, abo)

    df["HLA_antibodies"]=hla_antibodies_list
    df["cPRA"]= cpra_list
    df["TS"]= TS_list
    print("Generated " + str(total_samples) +  " recipients between timesteps " + str(min_timestep) + " and " + str(max_timestep) )
    # Preview
    df.to_csv(output_filepath, index=False)



