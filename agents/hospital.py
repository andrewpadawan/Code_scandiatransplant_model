from book_keeping.locations import city_country_map
from book_keeping.constants import organs
from agents.waiting_lists import LocalWaitList

import pandas as pd

class Hospital:
    registry = []
    def __init__(self, city, waitlist_df=None):
        self.city = city
        self.country = city_country_map.get(city, "Unknown")
        self.recipient_waiting_list = LocalWaitList(waitlist_df)
        self.donor_list = LocalWaitList(waitlist_df)
        #Each hospital will keep this table to keep track of the exchange obligations
        self.organ_exchange_table = pd.DataFrame(
            {city: [[] for _ in organs] for city in city_country_map.keys()},
            index=organs
        )
        #All hospitals self register on the registry on creation
        Hospital.registry.append(self)
    def print(self):
        print("*********************************")
        if self.city:
            print(f"City: {self.city}")
        if self.recipient_waiting_list is not None:
            print("Exchange duties:\n")
            print(self.organ_exchange_table.to_string(col_space=12))
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

    