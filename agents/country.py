from agents.waiting_lists import *
class Country:
    def __init__(self, name,hospitals= None, waitlist=None, list_donor=None):
        self.name= name
        self.waitlist = waitlist if waitlist is not None else CountryWaitList()
        self.donor_list = list_donor if list_donor is not None else CountryWaitList()
        self.member_hospitals= hospitals if hospitals is not None else []
    def print(self):
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(self.name + " overview:")
        print("Waitlist for "+ self.name + ": ")
        print(self.waitlist.df)
        print("Donor list for "+ self.name + ": ")
        print(self.donor_list.df)
        print("Member hospitals: ")
        for hos in self.member_hospitals:
            print("-" + hos.city)
        
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    def aggregate_waitlist(self):
        
        combined_df = pd.concat(
        [hos.recipient_waiting_list.df for hos in self.member_hospitals],
            ignore_index=True
        )
        combined_df.sort_values("RECIPIENTNUMBER", inplace=True)
        self.waitlist = CountryWaitList(combined_df)

    def aggregate_donorlist(self):
        combined_df = pd.concat(
        [hos.donor_list.df for hos in self.member_hospitals],
            ignore_index=True
        )
        combined_df.sort_values("DONORNUMBER", inplace=True)
        self.donor_list = CountryWaitList(combined_df)
    def aggregate_all_lists(self):
        self.aggregate_waitlist()
        self.aggregate_donorlist()
        