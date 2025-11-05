import random
from book_keeping import locations
import numpy as np
from collections import Counter
def generate_blood_types(abo_distribution, rh_distribution, total_samples):

    """
    Generates a list of blood types based on ABO and Rh distributions.

    Based on the values of Denmark from https://en.wikipedia.org/wiki/Blood_type_distribution_by_country 
    And Rh infor from https://givblod.dk/fakta-om-blod/blodtyperne/

    Parameters:
    - abo_distribution: dict with ABO types and their percentages (e.g., {'A': 40, 'O': 40, 'B': 15, 'AB': 5})
    - rh_distribution: dict with Rh types and their percentages (e.g., {'+': 85, '-': 15})
    - total_samples: number of blood type samples to generate

    Returns:
    - List of blood types like ['A+', 'O-', 'B+', ...]
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

    return all_timesteps
