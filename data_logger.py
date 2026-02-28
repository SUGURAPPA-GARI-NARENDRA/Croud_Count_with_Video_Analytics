import csv
import datetime

def log_data(zone_counts, entry, exit):
    with open("count_data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.datetime.now(),
            zone_counts,
            entry,
            exit
        ])