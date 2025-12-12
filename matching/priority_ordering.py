import pandas as pd
from utils.logger import get_matching_logger, log_match, log_match_csv_dynamic
from agents.organs import *
from typing import List
from agents.hospital import *

from match_utils import *

def ordering_priority_1(recipient_df, organ:Organ):
    """ If there is more than one STAMP candidate when doing the search for kidney exchange obligations the recipients must be prioritised in the following order 
    1. Lowest TS, ABO compatible
    2. ABO identical recipients
    3. Same country as donor
    4. Longest waiting time
    The search result list is sorted by a calculated AMP-score, which is a weight score based on these priorities.
    """
    #filter by ABO compatible, order by TS. Take the smallest TS (and all the recipients that have it. i.e if I have 5 people with TS=0.3, take all five and move to next step)
    abo_compatible_recipient_df= ABO_compatible_df(recipient_df, organ)
    TS_sorted_df = abo_compatible_recipient_df.sort_values(by="TS", ascending=True)

    min_ts = TS_sorted_df.iloc[0]["TS"]
    min_ts_rows = TS_sorted_df[recipient_df["TS"] == min_ts]

    #if I can find the ABO compatible recipient with minimum TS and its only 1, then I am done
    if len(min_ts_rows)== 1:
        return min_ts_rows
    
    #If not, filter the received dataframe by ABO identical recipients
    
    abo_identical= ABO_identical(organ, min_ts_rows)

    if len(abo_identical)==1:
        return abo_identical
    #filter the received dataframe by same country as donor
    same_country_df = abo_identical[abo_identical["COUNTRY"] == organ.country]
    if len(same_country_df)==1:
        return same_country_df
    #order received dataframe by longest waiting time (recipient number). This is unique so this will break any leftover ties
    ranked_by_id= same_country_df.sort_values(by="RECIPIENTNUMBER", ascending=True)
    return ranked_by_id.head(1)


def ordering_priority_2_to_5(recipient_df):
    print()
