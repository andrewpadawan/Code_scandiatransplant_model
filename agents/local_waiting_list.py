import pandas as pd

class localWaitList:
    def __init__(self, csv_path, country_code):
        self.country_code = country_code
        self.df = pd.read_csv(csv_path)
        self.waitList = self.filter_by_country()

    def filter_by_country(self):
        return self.df[self.df['Country'] == self.country_code]