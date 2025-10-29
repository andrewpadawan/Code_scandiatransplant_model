from book_keeping.locations import city_country_map
from agents.waiting_lists import LocalWaitList

import pandas as pd

class Hospital:
    registry = []
    def __init__(self, city, waitlist_df=None):
        self.city = city
        self.country = city_country_map.get(city, "Unknown")
        self.recipient_waiting_list = LocalWaitList(waitlist_df)
        self.donor_list = LocalWaitList(waitlist_df)
        #All hospitals self register on the registry on creation
        Hospital.registry.append(self)
    def print(self):
        if self.city:
            print(f"City: {self.city}")
        if self.recipient_waiting_list is not None:
            print(f"Local waiting list: {self.recipient_waiting_list.df}")