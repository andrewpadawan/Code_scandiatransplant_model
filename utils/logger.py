import logging
import os
from datetime import datetime
import csv

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


def log_match(logger, donor_df, recipient_df):
    donor_id = donor_df["DONORNUMBER"].values[0]
    donor_city = donor_df["CITY"].values[0]
    donor_country = donor_df["COUNTRY"].values[0]
    donor_blood = donor_df["AB0_BLOOD_GROUP"].values[0]
    donor_rhesus= donor_df["RHESUS_CODE"].values[0]
    donor_entry= donor_df["TIMESTEP_ENTERED"].values[0]

    recipient_id = recipient_df["RECIPIENTNUMBER"].values[0]
    recipient_city = recipient_df["CITY"].values[0]
    recipient_country = recipient_df["COUNTRY"].values[0]
    recipient_blood = recipient_df["AB0_BLOOD_GROUP"].values[0]
    recipient_rhesus= recipient_df["RHESUS_CODE"].values[0]
    recipient_entry= recipient_df["TIMESTEP_ENTERED"].values[0]

    match_log = (
       
        f"Donor {donor_id} (City: {donor_city}, Country: {donor_country}, Blood: {donor_blood}), Rhesus: {donor_rhesus}, Entered timestep: {donor_entry} \n"
        f"matched with Recipient {recipient_id} (City: {recipient_city}, Country: {recipient_country},  Blood: {recipient_blood}), Rhesus: {recipient_rhesus}, Entered timestep: {recipient_entry}"
    )

    logger.info(match_log)


def log_timestep(logger, timestep):
    header = f"\nTIMESTEP {timestep}\n" + "*" * 40
    logger.info(header)


def log_match_csv_dynamic(timestep, donor_df, recipient_df, log_timestamp):
    donor = donor_df.iloc[0]
    recipient = recipient_df.iloc[0]

    # Prefix columns to avoid collisions
    donor_cols = [f"DONOR_{col}" for col in donor_df.columns]
    recipient_cols = [f"RECIPIENT_{col}" for col in recipient_df.columns]
    all_headers = ["TIMESTEP"] + donor_cols + recipient_cols

    # Prepare row data
    row_data = [timestep] + list(donor.values) + list(recipient.values)

    # Build log path
    timestamp = log_timestamp
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