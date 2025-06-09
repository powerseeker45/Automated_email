import csv
import random
from datetime import datetime, timedelta

def generate_employee_csv(filename="employees.csv", num_employees=100):
    """
    Generate a CSV file with employee data
    
    Args:
        filename: Name of the CSV file to create
        num_employees: Number of employee records to generate
    """
    
    # Sample data for generating realistic employee records
    first_names = [
        "John", "Jane", "Michael", "Emily", "David", "Sarah", "Chris", "Lisa", 
        "James", "Maria", "Robert", "Jennifer", "William", "Linda", "Richard",
        "Patricia", "Charles", "Barbara", "Joseph", "Elizabeth", "Thomas", "Susan",
        "Christopher", "Jessica", "Daniel", "Margaret", "Matthew", "Dorothy", "Anthony",
        "Nancy", "Mark", "Betty", "Donald", "Helen", "Steven", "Sandra", "Paul",
        "Donna", "Andrew", "Carol", "Joshua", "Ruth", "Kenneth", "Sharon", "Kevin",
        "Michelle", "Brian", "Laura", "George", "Sarah", "Edward", "Kimberly"
    ]
    
    last_names = [
        "Doe", "Smith", "Brown", "Davis", "Wilson", "Miller", "Moore", "Taylor",
        "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson",
        "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee",
        "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez",
        "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter",
        "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker",
        "Evans", "Edwards", "Collins", "Stewart", "Sanchez", "Morris", "Rogers"
    ]
    
    departments = [
        "HR", "Finance", "Engineering", "Marketing", "Operations", "Sales",
        "IT", "Legal", "Administration", "Customer Service", "Research", "Quality Assurance"
    ]
    
    # Open CSV file for writing
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['first_name', 'last_name', 'email', 'birthday', 'anniversary', 'department'])
        
        # Generate employee records
        for i in range(num_employees):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            # Generate email
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            
            # Generate random birthday (between 1970 and 2000)
            start_date = datetime(1970, 1, 1)
            end_date = datetime(2000, 12, 31)
            random_birthday = start_date + timedelta(
                days=random.randint(0, (end_date - start_date).days)
            )
            birthday = random_birthday.strftime('%Y-%m-%d')
            
            # Generate random anniversary (50% chance of having one)
            if random.random() < 0.5:  # 50% chance
                # Anniversary between 2010 and 2023
                start_anniversary = datetime(2010, 1, 1)
                end_anniversary = datetime(2023, 12, 31)
                random_anniversary = start_anniversary + timedelta(
                    days=random.randint(0, (end_anniversary - start_anniversary).days)
                )
                anniversary = random_anniversary.strftime('%Y-%m-%d')
            else:
                anniversary = "NA"
            
            # Random department
            department = random.choice(departments)
            
            # Write row
            writer.writerow([first_name, last_name, email, birthday, anniversary, department])
    
    print(f"✅ Generated {num_employees} employee records in '{filename}'")
    print(f"📄 File location: {filename}")

def generate_specific_csv():
    """
    Generate the exact CSV data as specified in the example
    """
    filename = "employees_example.csv"
    
    # Exact data as specified
    employees_data = [
        ["John", "Doe", "john.doe@example.com", "2025-06-09", "2025-06-09", "HR"],
        ["Jane", "Smith", "jane.smith@example.com", "2025-06-09", "NA", "Finance"],
        ["Michael", "Brown", "michael.brown@example.com", "2025-06-09", "2025-06-09", "Engineering"],
        ["Emily", "Davis", "emily.davis@example.com", "2025-06-09", "NA", "Marketing"],
        ["David", "Wilson", "david.wilson@example.com", "2025-06-09", "2025-06-09", "Operations"]
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['first_name', 'last_name', 'email', 'birthday', 'anniversary', 'department'])
        
        # Write employee data
        for employee in employees_data:
            writer.writerow(employee)
    
    print(f"✅ Generated exact example CSV: '{filename}'")
    return filename

def generate_today_birthdays_csv(num_today=5):
    """
    Generate CSV with some employees having birthdays today for testing
    """
    filename = "employees_test_today.csv"
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Sample employees with today's birthday for testing
    todays_employees = [
        ["Alex", "Johnson", "alex.johnson@example.com", today, "2020-03-15", "IT"],
        ["Sophie", "Williams", "sophie.williams@example.com", today, "NA", "Sales"],
        ["Mark", "Taylor", "mark.taylor@example.com", today, today, "HR"],
        ["Lisa", "Anderson", "lisa.anderson@example.com", today, "2019-09-22", "Marketing"],
        ["Ryan", "Thomas", "ryan.thomas@example.com", today, "NA", "Finance"]
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['first_name', 'last_name', 'email', 'birthday', 'anniversary', 'department'])
        
        # Write today's birthday employees
        for employee in todays_employees[:num_today]:
            writer.writerow(employee)
    
    print(f"✅ Generated test CSV with {num_today} birthdays today: '{filename}'")
    return filename

def main():
    """
    Main function to generate different types of CSV files
    """
    print("🎯 Employee CSV Generator")
    print("=" * 50)
    
    # Generate the exact example CSV
    print("\n1. Generating exact example CSV...")
    generate_specific_csv()
    
    # Generate a larger random CSV
    print("\n2. Generating random employee CSV (100 records)...")
    generate_employee_csv("employees_random.csv", 100)
    
    # Generate test CSV with today's birthdays
    print("\n3. Generating test CSV with today's birthdays...")
    generate_today_birthdays_csv(5)
    
    print("\n✨ All CSV files generated successfully!")
    print("\nFiles created:")
    print("- employees_example.csv (exact example data)")
    print("- employees_random.csv (100 random employees)")
    print("- employees_test_today.csv (5 employees with today's birthday)")

if __name__ == "__main__":
    main()