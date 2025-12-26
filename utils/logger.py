import logging
import os
from datetime import datetime
import csv
from agents.organs import *

def get_matching_logger(name="matching_logger"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"matching_{timestamp}.log"
    log_path = os.path.join("logs/text_logs", log_filename)

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('- %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_match(logger, organ: Organ, recipient_df, priority_level_assigned= 0):
    donor_id = organ.donor_id
    organ_city = organ.city
    organ_country = organ.country
    organ_blood= organ.abo_blood
    organ_rhesus= organ.rhesus
    organ_entry= organ.timestep
    organ_type= organ.type
    exchange_obligation= organ.exchange_obligation

    recipient_id = recipient_df["RECIPIENTNUMBER"].values[0]
    recipient_city = recipient_df["CITY"].values[0]
    recipient_country = recipient_df["COUNTRY"].values[0]
    recipient_blood = recipient_df["ABO_BLOOD_GROUP"].values[0]
    recipient_rhesus= recipient_df["RHESUS_CODE"].values[0]
    recipient_entry= recipient_df["TIMESTEP_ENTERED"].values[0]

    match_log = (
        
        f"Exchange obligation: {exchange_obligation} with priority level {priority_level_assigned}\n"
        f"Organ {organ_type} (City: {organ_city}, Country: {organ_country}, Blood: {organ_blood}), Entered timestep: {organ_entry} from Donor {donor_id} \n"
        f"matched with Recipient {recipient_id} (City: {recipient_city}, Country: {recipient_country},  Blood: {recipient_blood}),  Entered timestep: {recipient_entry} \n"
    )

    logger.info(match_log)


def log_timestep(logger, timestep):
    header = f"\nTIMESTEP {timestep}\n" + "*" * 40
    logger.info(header)


def log_match_csv_dynamic(timestep, organ, donor_row, recipient_df, log_timestamp, priority_level_assigned= 0):
    # Convert donor_row (Series) to single-row DataFrame
    donor_df = donor_row.to_frame().T

    # Prefix columns to avoid collisions
    donor_cols = [f"DONOR_{col}" for col in donor_df.columns]
    recipient_cols = [f"RECIPIENT_{col}" for col in recipient_df.columns]

    # Add organ-specific columns
    organ_cols = ["ORGAN_ID", "ORGAN_TYPE", "EXCHANGE_OBLIGATION", "PRIORITY_GROUP"]
    all_headers = ["TIMESTEP"] + organ_cols + donor_cols + recipient_cols

    # Prepare row data
    organ_data = [organ.organ_id, organ.type, organ.exchange_obligation, priority_level_assigned ]
    donor_values = list(donor_df.iloc[0].values)
    recipient_values = list(recipient_df.iloc[0].values)
    row_data = [timestep] + organ_data + donor_values + recipient_values

    # Build log path
    log_filename = f"matching_{log_timestamp}.csv"
    log_path = os.path.join("logs/csv_logs", log_filename)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Write to CSV
    file_exists = os.path.isfile(log_path)
    with open(log_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(all_headers)
        writer.writerow(row_data)

    return log_path