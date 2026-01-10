import random
import pandas as pd
from patient_generators.generating_utils import *

from patient_generators.generating_constants import *


def generate_donor(total_samples, min_timestep, max_timestep, output_filepath):
    abo, rh = generate_blood_types(abo_dist, rh_dist, total_samples)
    city_list, country_list = generate_locations(total_samples)
    donor_ids= []


    for i in range(len(abo)):
        donor_ids.append("D" + str(i).zfill(4))

    # Make my pandas df
    headers = ['DONORNUMBER', 'ABO_BLOOD_GROUP', 'RHESUS_CODE', 'GRAFT_TYPE',"AGE", "CITY", "COUNTRY", "TIMESTEP_ENTERED", "Genomic_HLA-A","Genomic_HLA-B","Genomic_HLA-C","Genomic_HLA-DRB1","Genomic_HLA-DQA1","Genomic_HLA-DQB1","Genomic_HLA-DPA1" ,"Genomic_HLA-DPB1","Serologic_HLA-A","Serologic_HLA-B","Serologic_HLA-C","Serologic_HLA-DRB1","Serologic_HLA-DQA1","Serologic_HLA-DQB1","Serologic_HLA-DPA1" ,"Serologic_HLA-DPB1",'Notes']
    df = pd.DataFrame(columns=headers)

    
    
    df["DONORNUMBER"]= donor_ids
    df["ABO_BLOOD_GROUP"]= abo
    df["RHESUS_CODE"] = rh
    #For now all organs are kidneys. The proper way KD: Double Kidney;KL: Left Kidney;KR: Right
    df["GRAFT_TYPE"]= "KD"
    df["AGE"]= generate_donor_ages(total_samples)
    df["CITY"]= city_list
    df["COUNTRY"]= country_list
    df["TIMESTEP_ENTERED"]= generate_timesteps(total_samples, 0, min_timestep, max_timestep)
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

    print(df.head())
    # Preview
    print("Generated " + str(total_samples) +  " donors between timesteps " + str(min_timestep) + " and " + str(max_timestep) )
    df.to_csv(output_filepath, index=False)

    




