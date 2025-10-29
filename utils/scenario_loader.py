import json
import pandas as pd
from agents.hospital import Hospital
from agents.waiting_lists import *
from agents.scandiatransplant import *
from agents.country import *
from book_keeping import locations

def load_scenario(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    hospitals = [Hospital(entry["city"]) for entry in data["hospital"]]

    scandiatransplant,  df_ALL_recipients, df_ALL_donors= load_local_waiting_list(data, hospitals)
    for country in scandiatransplant.member_countries:
        country.aggregate_all_lists()
    scandiatransplant.aggregate_all_lists()


    return scandiatransplant, hospitals,  df_ALL_recipients, df_ALL_donors

def load_local_waiting_list(data, hospitals):
    #filepath for the recipient list

    relevant_countries = {locations.city_country_map[hos.city] for hos in hospitals if hos.city in locations.city_country_map}
    
    recipient_list= data["recipient_list"]
    donor_list= data["donor_list"]

        # Load CSV into DataFrame
    try:
        df_recipients = pd.read_csv(recipient_list)
        df_donors = pd.read_csv(donor_list)
  
        
    except FileNotFoundError:
        print(f"File not found: {recipient_list} or {donor_list}")
    except pd.errors.EmptyDataError:
        print(f"File is empty or unreadable: {recipient_list} or {donor_list}")
    except Exception as e:
        print(f"Error loading recipient list: {e}")
    
    #print(df)
  

    for hos in hospitals:
        filtered_df = df_recipients[
        (df_recipients["CITY"] == hos.city) & (df_recipients["TIMESTEP_ENTERED"] == 0)
        ]
        donor_filtered_df = df_donors[
            (df_donors["CITY"] == hos.city) & (df_donors["TIMESTEP_ENTERED"] == 0)
        ]

        hos.recipient_waiting_list= LocalWaitList(hos.city, filtered_df)
        hos.donor_list= LocalWaitList(hos.city, donor_filtered_df)
    
    country_map = {}
    for hos in hospitals:
        country_name = hos.country
        if country_name not in country_map:
            country_map[country_name] = Country(name=country_name, hospitals=[])
        country_map[country_name].member_hospitals.append(hos)

    # Step 4: Create Scandiatransplant object with countries
    countries = list(country_map.values())
    scandiatransplant = Scandiatransplant(countries=countries)

    return scandiatransplant, df_recipients, df_donors
    
    """  scandiatransplant= Scandiatransplant(hospitals, ScandiatransplantWaitList(pd.read_csv(recipient_list)))

    for count in relevant_countries:
        scandiatransplant.member_countries.append(Country(count))

        for hos in hospitals:
            if hos.country == count:
                count.member_hospitals.append(hos)
         """
        # Step 3: Group hospitals by country and create Country objects





    