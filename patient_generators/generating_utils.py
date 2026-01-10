import random
from book_keeping import locations
import numpy as np
from collections import Counter
from patient_generators.generating_constants import *
import copy
from scipy.stats import truncnorm
from scipy.stats import beta
from scipy.optimize import minimize
import pandas as pd

abo_compatibility_receive = {
    "O": ["O"],                  
    "A": ["A", "O"],             
    "B": ["B", "O"],             
    "AB": ["A", "B", "AB", "O"], 
}

def generate_blood_types(abo_distribution, rh_distribution, total_samples):

    """

    Based on the values of Denmark from https://en.wikipedia.org/wiki/Blood_type_distribution_by_country 
    And Rh infor from https://givblod.dk/fakta-om-blod/blodtyperne/

    """

    # Normalize distributions
    def normalize(dist):
        total = sum(dist.values())
        return {k: v / total for k, v in dist.items()}

    abo_probs = normalize(abo_distribution)
    rh_probs = normalize(rh_distribution)

    
    abo_choices = list(abo_probs.keys())
    abo_weights = list(abo_probs.values())

    rh_choices = list(rh_probs.keys())
    rh_weights = list(rh_probs.values())

    
    abo_list= []
    rh_list= []
    
    for _ in range(total_samples):
        abo_list.append(random.choices(abo_choices, weights=abo_weights, k=1)[0])
        rh_list.append(random.choices(rh_choices, weights=rh_weights, k=1)[0])


    #print(abo_list, rh_list)
    return abo_list, rh_list



def generate_locations(total_samples, seed=None):
    # I assume that donor and recipient numbers are proportional to population
    if seed is not None:
        random.seed(seed)

    cities = list(locations.city_pop.keys())
    populations = list(locations.city_pop.values())
    total_pop = sum(populations)
    weights = [pop / total_pop for pop in populations]

    generated_cities = random.choices(cities, weights=weights, k=total_samples)
    random.shuffle(generated_cities)  # Shuffle to avoid clustering

    city_list = generated_cities
    country_list = [locations.city_country_map.get(city, "Unknown") for city in generated_cities]

    return city_list, country_list


def generate_timesteps(total_samples, zero_fraction=0.6, min_timestep=1, max_timestep=365):
    print("Generating timesetps")
    # Calculate how many should have timestep 0
    zero_count = int(total_samples * zero_fraction)

    # Assign timestep 0
    fixed_timesteps = [0] * zero_count

    # Uniformly distribute the rest
    remaining_count = total_samples - zero_count
    random_timesteps = np.random.randint(min_timestep, max_timestep + 1, size=remaining_count)

    # Combine and order: I want the list to have an ascending timestep and id numbers, where the timesteps are random
    all_timesteps = fixed_timesteps + list(random_timesteps)
    all_timesteps.sort()  # Sort in ascending order
    #np.random.shuffle(all_timesteps)
    print("Done")
    return all_timesteps

def generate_recipient_ages(total_samples, seed=None):
    print("Generating recipient ages")
    if seed is not None:
        np.random.seed(seed)

    # Normalize incidence to get probabilities
    incidences = np.array(incidence_recipients)
    probs = incidences / incidences.sum()

    # Sample age group indices
    group_indices = np.random.choice(len(age_groups_recipients), size=total_samples, p=probs)

    # Sample age within each selected group
    sampled_ages = np.array([
        np.random.randint(*age_groups_recipients[i]) + 1  # safer unpacking
        for i in group_indices
    ])
    np.random.shuffle(sampled_ages)
    print("Done")
    return sampled_ages

def generate_donor_ages(total_samples, seed=None):
    if seed is not None:
        np.random.seed(seed)

    # Normalize incidence to get probabilities
    incidences = np.array(incidence_donors)

    # Sample age group indices
    group_indices = np.random.choice(len(age_groups_donors), size=total_samples, p=incidences)

    # Sample age within each selected group
    sampled_ages = np.array([
        np.random.randint(*age_groups_donors[i]) + 1  # safer unpacking
        for i in group_indices
    ])
    np.random.shuffle(sampled_ages)

    return sampled_ages

def generate_hla_genotypes(total_samples):
    print("Generating HLA genotypes")
    genotypes = {locus: [] for locus in hla_frequencies.keys()}
    serology  = {locus: [] for locus in hla_frequencies.keys()}
    
    for _ in range(total_samples):
        for locus, alleles in hla_frequencies.items():
            names, weights = zip(*alleles)
            sampled = random.choices(names, weights=weights, k=2)
            np.random.shuffle(sampled)
            genotypes[locus].append(list(sampled))
            
            # Translate to serology
            translated = []
            for allele in sampled:
                sero = hla_to_serologic.get(locus, {}).get(allele)
                if sero:
                    translated.append(sero)
                else:
                    translated.append(f"Unknown({allele})")
            serology[locus].append(translated)
    print("DOne")
    return genotypes, serology

def generate_recipient_antibodies(total_samples, hla_serology, abo):
    print("Generating antibodies")
    all_patient_antibodies= []
    all_patient_cPRA= []
    all_patients_TS= []
    #get all the antigens in a list to get ready to sample
    sero_to_gene= build_serologic_to_genetic(hla_to_serologic)
    all_serologic = []
    for locus, allele_map in hla_to_serologic.items():
        all_serologic.extend(allele_map.values())

    for patient_index in range(total_samples):
        print("Generating antibodies for recipient" + str(patient_index))
        patient_serology = get_patient_serology_list(hla_serology, patient_index)[0]
        my_all_serologic= [antigen for antigen in all_serologic if antigen not in patient_serology]
        my_allele_freq= 0
        my_antigen_list = []
        cpra= sample_cPRA_uniform()
        
        #if cpra is exactly zero, then the allele_freq should remain exactly so
        if cpra == 0:
            my_allele_freq= 0
        else:
            attempts = 0
            
            while True:
                attempts += 1
                # If we tried 10 times, force accept whatever we have 

                #I sample a random antigen from the dictionary, get the gene, get the allele freq
                sample= random.choice(my_all_serologic)
                genes = sero_to_gene.get(sample, [])
                if not genes:
                    continue  # skip if no mapping found
                gene = random.choice(genes)

                #Not sample same antibody twice or more
                if gene in my_antigen_list:
                    continue

                gene_freq= check_gene_frequency(gene)

                if attempts >= 10: 
                    if my_allele_freq <= 1:
                    # Stop trying, keep whatever we have so far
                        break

                if (my_allele_freq + gene_freq > cpra + 0.02) or (my_allele_freq + gene_freq > 1): #I'm giving a bit of leeway sop +0.001, but otherwise resample
                    continue
                else:
                    my_allele_freq= my_allele_freq + gene_freq
                    #my_antigen_list.append(gene)
                    if isinstance(gene, str):
                        my_antigen_list.append(gene)
                    else:
                        # Convert numeric allele codes to strings
                        my_antigen_list.append(str(gene))


                    my_all_serologic.remove(sample)

                if my_allele_freq > cpra - 0.001: #also a bit of rounding for ease
                    break

                
                


        all_patient_antibodies.append(my_antigen_list)
        all_patient_cPRA.append(round(my_allele_freq, 6))

        #Use the just calculated cPRA and the abo info to calculate TS
        all_patients_TS.append(calculate_TS(my_allele_freq, abo[patient_index] ))
    print("Done")
    return all_patient_antibodies, all_patient_cPRA, all_patients_TS

def calculate_TS(cPRA, abo_group):
    compatible_abo= abo_compatibility_receive.get(abo_group, [])
    compatible_total = sum(abo_dist[group] for group in compatible_abo)
    compatible_pct = compatible_total/100

    TS_score= compatible_pct* (1-cPRA)
    return TS_score


def check_gene_frequency(gene):
    
    locus = gene.split("*")[0] if "*" in gene else None

    # Check frequency for this gene in hla_frequencies
    if locus and locus in hla_frequencies:
        for allele, freq in hla_frequencies[locus]:
            if allele == gene:
               return freq
    return 0.0

def get_patient_serology_list(serology, patient_index):
    patient_values = []
    for locus in serology.keys():
        patient_values.extend(serology[locus][patient_index])
    return patient_values



def choose_HS_patients(total_samples):
    #probability HS is 14%
    return [random.random() < 0.14 for _ in range(total_samples)]


def build_serologic_to_genetic(hla_to_serologic):
    """
    Invert the mapping so you can check what allele(s) correspond
    to each serologic shorthand.
    """
    serologic_to_genetic = {}
    
    for locus, allele_map in hla_to_serologic.items():
        for genetic, sero in allele_map.items():
            # Initialize if not seen before
            if sero not in serologic_to_genetic:
                serologic_to_genetic[sero] = []
            serologic_to_genetic[sero].append(genetic)
    
    return serologic_to_genetic


def check_if_acceptable_mismatch(donor_row: pd.Series, recipient: dict) -> bool:
    #acceptable mismatch if the recipient doenst have antibodies against the donor antigens
    # Define the relevant donor HLA columns
    hla_columns = [
        "Serologic_HLA-A",
        "Serologic_HLA-B",
        "Serologic_HLA-C",
        "Serologic_HLA-DRB1",
        "Serologic_HLA-DQA1",
        "Serologic_HLA-DQB1",
        "Serologic_HLA-DPA1",
        "Serologic_HLA-DPB1"
    ]
    
    # Extract donor antigens into a list
    donor_antigens = [donor_row.get(col, None) for col in hla_columns if donor_row.get(col, None) is not None]
    
    # Get recipient antibodies list
    recipient_antibodies = recipient.get("HLA_antibodies", [])
    
    # Check compatibility: return True if no overlap
    return not any(antigen in recipient_antibodies for antigen in donor_antigens)



def sample_cPRA_uniform(n_samples=1, percent_output=False, seed=None):
    """
    Sample cPRA using a uniform mixture over predefined intervals with given weights.

    Intervals (in %):
      - [0, 0]       with weight 0.62
      - [1, 20]      with weight 0.08
      - [21, 79]     with weight 0.14
      - [80, 97]     with weight 0.05
      - [98, 100]    with weight 0.09

    Parameters
    ----------
    n_samples : int
        Number of samples to generate.
    percent_output : bool
        If True, return values in 0–100 (%). If False, return proportions 0–1.
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    np.ndarray
        Array of cPRA values (proportion 0–1 by default, or % if percent_output=True).
    """
    if seed is not None:
        np.random.seed(seed)

    # Define interval edges in percent
    intervals = [
        (0.0, 0.0, 0.62),   # exact zero
        (1.0, 20.0, 0.08),
        (21.0, 79.0, 0.14),
        (80.0, 97.0, 0.05),
        (98.0, 100.0, 0.09),
    ]

    # Mixture selection
    weights = np.array([w for _, _, w in intervals], dtype=float)
    weights = weights / weights.sum()  # safety normalization

    # Choose intervals
    choices = np.random.choice(len(intervals), size=n_samples, p=weights)

    # Sample uniformly within chosen interval
    samples_percent = np.empty(n_samples, dtype=float)
    for i, idx in enumerate(choices):
        lo, hi, _ = intervals[idx]
        if lo == hi:  # exact zero bin
            samples_percent[i] = 0.0
        else:
            samples_percent[i] = np.random.uniform(lo, hi)

    # Return as proportion or percent
    if percent_output:
        return samples_percent
    else:
        return samples_percent / 100.0


from typing import List

def assign_bw4_bw6_bulk(hla_a_list: List[List[str]], hla_b_list: List[List[str]]) -> List[str]:
    # Define Bw4 and Bw6 sets
    bw4 = bw4_mapping

    bw6 = bw6_mapping

    def normalize(antigen):
        return antigen.split("(")[0]

    bw_status_list = []

    for a_antigens, b_antigens in zip(hla_a_list, hla_b_list):
        bw4_count = 0
        bw6_count = 0
        all_antigens = a_antigens + b_antigens

        for antigen in all_antigens:
            norm = normalize(antigen)
            if antigen in bw4 or norm in bw4:
                bw4_count += 1
            elif antigen in bw6 or norm in bw6:
                bw6_count += 1

        if bw4_count == 2:
            bw_status_list.append("Bw4/Bw4")
        elif bw4_count == 1:
            bw_status_list.append("Bw4/Bw6")
        else:
            bw_status_list.append("Bw6/Bw6")

    return bw_status_list
