import csv
import datetime
import os

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "count_data.csv")

def log_data(zone_counts, entry, exit_count):
    # Check if file exists to write header
    file_exists = os.path.isfile(CSV_PATH)
    
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        
        # Define the header
        # We extract zone names to make them individual columns
        zone_names = list(zone_counts.keys())
        header = ["Timestamp", "Entry_Count", "Exit_Count", "Total_Inside"] + zone_names
        
        if not file_exists:
            writer.writerow(header)

        # Prepare the row data
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_inside = entry - exit_count
        
        # Create a list of counts for each zone in the same order as header
        zone_values = [zone_counts.get(name, 0) for name in zone_names]
        
        row = [timestamp, entry, exit_count, total_inside] + zone_values
        writer.writerow(row)