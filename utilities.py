import os
import csv

def update_csv_file(filename, new_data, input_header):
    """
    Updates csv 'filename' by appending nested list 'new_data'. First row must be unique ID. Forces uppercase headers.
    """

    new_header = [x.upper() for x in input_header]

    # Check if file exists
    if not os.path.isfile(filename):
        # Create file with header row
        header = new_header
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
        print(f"File '{filename}' created with header row: ", new_header)

    # Read in existing data from file
    data = []
    with open(filename, 'r', newline='') as file:
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
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        for row in new_data:
            if row[0] not in existing_ids:
                writer.writerow(row)

    data_added = [row for row in new_data if row[0] not in existing_ids]

    print(f"{len(data_added)} rows of data written to '{filename}'.")
