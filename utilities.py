import os
import csv
import datetime as dt

def start_timer():
    global start_time
    start_time = dt.datetime.now()
    print('Start time: ', start_time.strftime('%H:%M:%S'))
    return start_time

def end_timer():
    end_time = dt.datetime.now()
    print('End time: ', end_time.strftime('%H:%M:%S'))
    runtime = end_time - start_time
    print('Runtime: ', runtime,'\n')

def update_csv_file(filename, new_data, input_header):
    """
    Updates csv 'filename' by appending nested list 'new_data'. First row must be unique ID. Forces uppercase headers.
    """

    new_header = [x.upper() for x in input_header]

    # Check if file exists
    if not os.path.isfile(filename):
        # Create file with header row
        header = new_header
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)
        print(f"File '{filename}' created with header row: ", new_header)

    # Read in existing data from file
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

        # Check if header from existing data matches header for new data
        existing_header = data[0]
        if existing_header != new_header:
            raise ValueError(f"Header in file '{filename}' does not match header for new data.")


    # Check if new data already exists in file
    new_ids = {row[0] for row in new_data[1:]}
    existing_ids = {row[0] for row in data[1:]}
    common_ids = new_ids & existing_ids
    if common_ids:
        print(f"{len(common_ids)} IDs already exist in file '{filename}'. Skipping ID's present.")

    # Append new data to file
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in new_data:
            if row[0] not in existing_ids:
                writer.writerow(row)

    data_added = [row for row in new_data if row[0] not in existing_ids]

    print(f"{len(data_added)} rows of data written to '{filename}'.")

def check_id_in_csv(csv_filename, unique_id):
    if not os.path.isfile(csv_filename):
        # print(f"File {csv_filename} does not exist.")
        return False

    with open(csv_filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == unique_id:
                return True
    return False

def check_date_range(start_date, end_date):
    # check date format
    try:
        dt.datetime.strptime(start_date, '%Y-%m-%d')
        dt.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be yyyy-mm-dd")

    # check date range
    start = dt.datetime.strptime(start_date, '%Y-%m-%d')
    end = dt.datetime.strptime(end_date, '%Y-%m-%d')
    today = dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if start > end:
        raise ValueError("Start date must come before end date")
    elif start > today or end > today:
        raise ValueError("Dates must be before or on today")
    else:
        return True
