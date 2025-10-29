import pandas as pd

class WaitList:
    def __init__(self, df=None):
        self.df = df if df is not None else pd.DataFrame()
    def get_size(self):
        return len(self.df)
    def sort(self, header):
        self.df.sort_values(by=str(header), inplace=True)
        #print(self.df)
class LocalWaitList(WaitList):
    def __init__(self, city, df=None):
        super().__init__(df)
        self.city= city

class CountryWaitList(WaitList):
    def __init__(self, df=None):
        super().__init__(df)

class ScandiatransplantWaitList(WaitList):
    def __init__(self, df=None):
        super().__init__(df)





#Functions for waiting list functionalities:

