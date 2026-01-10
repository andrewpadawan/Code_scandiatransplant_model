from agents.waiting_lists import *
from collections import deque

class Scandiatransplant:
    def __init__(self, countries= None, waitlist=None, waitlist2=None, waitlist3=None, hospitals= None):
        self.recipient_waitlist = waitlist if waitlist is not None else ScandiatransplantWaitList()
        self.donor_list = waitlist2 if waitlist2 is not None else ScandiatransplantWaitList()
        self.organ_list = waitlist3 if waitlist3 is not None else []
        self.member_countries= countries if countries is not None else []
        
        self.rota = deque(sorted(hospitals, key=lambda h: h.city))
        self.unmatched_organs= []

    def print(self):
        print("**************************************************************")
        print("Scandiatransplant Overview")
        total_hospitals = sum(len(country.member_hospitals) for country in self.member_countries)
        print(f"Total member hospitals: {total_hospitals}")
        print(f"Total member countries: {len(self.member_countries)}")
        print(f"Central waiting list size: {self.recipient_waitlist.get_size()}")
        print(f"Central donor list size: {self.donor_list.get_size()}")
        print("\nMember hospitals:")
        for country in self.member_countries:
            for hos in country.member_hospitals:
                print(f" - {hos.city} ({hos.country}), {hos.recipient_waiting_list.get_size()} recipients")
        print("Organ list: " )
        print([o.organ_id for o in self.organ_list])
        print("UNMATCHED organ list: " )
        print([o.organ_id for o in self.unmatched_organs])
        print("**************************************************************")
   
   #Aggregations for waiting lists 

    def aggregate_waitlist(self):
        combined_df = pd.concat(
            [country.waitlist.df for country in self.member_countries],
            ignore_index=True
        )
        # Sort by RECIPIENTNUMBER
        combined_df.sort_values("RECIPIENTNUMBER", inplace=True)
        self.recipient_waitlist.df = combined_df

    def aggregate_donorlist(self):
        combined_df = pd.concat(
        [country.donor_list.df for country in self.member_countries],
        ignore_index=True
        )
        # Sort by DONORNUMBER
        combined_df.sort_values("DONORNUMBER", inplace=True)
        self.donor_list.df = combined_df


    def aggregate_all_lists(self):
        self.aggregate_waitlist()
        self.aggregate_donorlist()
    # Remove operations

    def remove_recipient(self, recipient_id, verbose=False):
        removed = False
        scandiatransplant_df = self.recipient_waitlist.df

        patient_row = scandiatransplant_df[scandiatransplant_df["RECIPIENTNUMBER"] == recipient_id]

        if patient_row.empty:
            if verbose:
                print(f"No patient with ID {recipient_id} exists in the Scandiatransplant waitlist.")
            return False
        else:
            city = patient_row["CITY"].values[0]
            recipient_country = patient_row["COUNTRY"].values[0]

        for country in self.member_countries:
            for hospital in country.member_hospitals:
                if hospital.city == city:
                    hospital.recipient_waiting_list.df = hospital.recipient_waiting_list.df[
                        hospital.recipient_waiting_list.df["RECIPIENTNUMBER"] != recipient_id
                    ]
                    removed = True
                    country.aggregate_waitlist()
                    break

        self.aggregate_waitlist()

        if verbose:
            if removed:
                print(f"✅ Patient {recipient_id} removed from all levels.")
            else:
                print(f"⚠️ Patient {recipient_id} not found in any hospital.")

        return removed


    def remove_donor(self, donor_id, verbose=False):
        removed = False
        scandiatransplant_df = self.donor_list.df

        patient_row = scandiatransplant_df[scandiatransplant_df["DONORNUMBER"] == donor_id]

        if patient_row.empty:
            if verbose:
                print(f"No donor with ID {donor_id} exists in the Scandiatransplant waitlist.")
            return False
        else:
            city = patient_row["CITY"].values[0]
            donor_country = patient_row["COUNTRY"].values[0]

        for country in self.member_countries:
            for hospital in country.member_hospitals:
                if hospital.city == city:
                    hospital.donor_list.df = hospital.donor_list.df[
                        hospital.donor_list.df["DONORNUMBER"] != donor_id
                    ]
                    removed = True
                    country.aggregate_donorlist()
                    break

        self.aggregate_donorlist()

        if verbose:
            if removed:
                print(f"✅ Patient {donor_id} removed from all levels.")
            else:
                print(f"⚠️ Patient {donor_id} not found in any hospital.")

        return removed


    #Add operations

    def add_recipient(self, recipient, verbose=False):
        added = False
        patient_row = recipient
        recipient_id = patient_row["RECIPIENTNUMBER"].values[0]

        if verbose:
            print(recipient_id)

        if patient_row.empty:
            if verbose:
                print(f"Empty recipient info")
            return False
        else:
            city = patient_row["CITY"].values[0]
            recipient_country = patient_row["COUNTRY"].values[0]

        for country in self.member_countries:
            for hospital in country.member_hospitals:
                if hospital.city == city:
                    hospital.recipient_waiting_list.df = pd.concat(
                        [hospital.recipient_waiting_list.df, patient_row], ignore_index=True
                    )
                    added = True
                    country.aggregate_waitlist()
                    break

        self.aggregate_waitlist()

        if verbose:
            if added:
                print(f"Recipient {recipient_id} added to all levels.")
            else:
                print(f"Failed to add patient {recipient_id}.")

        return added

        
    def add_donor(self, donor, verbose=False):
        added = False
        patient_row = donor
        donor_id = patient_row["DONORNUMBER"].values[0]

        if verbose:
            print(donor_id)

        if patient_row.empty:
            if verbose:
                print(f"Empty donor info")
            return False
        else:
            city = patient_row["CITY"].values[0]
            donor_country = patient_row["COUNTRY"].values[0]

        for country in self.member_countries:
            for hospital in country.member_hospitals:
                if hospital.city == city:
                    hospital.donor_list.df = pd.concat(
                        [hospital.donor_list.df, patient_row], ignore_index=True
                    )
                    added = True
                    country.aggregate_donorlist()
                    break

        self.aggregate_donorlist()

        if verbose:
            if added:
                print(f"Donor {donor_id} added to all levels.")
            else:
                print(f"Failed to add patient {donor_id}.")

        return added

    def remove_organ_by_id(self, organ_id):
        self.organ_list = [o for o in self.organ_list if o.organ_id != organ_id]

    def get_next_hospital(self, offering_hospital):
        """
        Returns the next hospital in the rota that is NOT the offering hospital.
        Moves the chosen hospital to the bottom of the rota.
        """
        for _ in range(len(self.rota)):  # one full cycle max
            candidate = self.rota[0]

            if candidate != offering_hospital:
                # Accept → rotate so candidate goes to bottom
                self.rota.rotate(-1)
                return candidate

            # Skip → rotate and continue
            self.rota.rotate(-1)

        return None  # no eligible hospital
