import csv
from datetime import date

# Get today's date in YYYY-MM-DD format
today = date.today().isoformat()

# Sample data using today's date
data = [
    ["John", "Doe", "john.doe@example.com", today, today, "HR"],
    ["Jane", "Smith", "jane.smith@example.com", today, "NA", "Finance"],
    ["Michael", "Brown", "michael.brown@example.com", today, today, "Engineering"],
    ["Emily", "Davis", "emily.davis@example.com", today, "NA", "Marketing"],
    ["David", "Wilson", "david.wilson@example.com", today, today, "Operations"],
]

# Define header
header = ["first_name", "last_name", "email", "birthday", "anniversary", "department"]

# Write to CSV file
with open("employees.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(data)

print("CSV file 'employees.csv' created successfully with today's dates.")
