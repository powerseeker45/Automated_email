import pandas as pd
def create_csv():
    """Create a sample CSV file for testing"""
    sample_data = {
        'empid': ['EMP001', 'EMP002', 'EMP003', 'EMP004'],
        'first_name': ['Alice', 'Bob', 'Carol', 'David'],
        'second_name': ['Johnson', 'Smith', 'Davis', 'Wilson'],
        'email': ['shashwat.airtel@gmail.com', 'shashwat.airtel@gmail.com', 'shashwat.airtel@gmail.com', 'shashwat.airtel@gmail.com'],
        'dob': ['1990-06-02', '1985-06-03', '1992-06-02', '1988-06-03'],  # Today's and tomorrow's dates for testing
        'department': ['Engineering', 'Marketing', 'HR', 'Engineering']
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('employees.csv', index=False)
    print("Sample CSV file 'employees.csv' created!")
    print("CSV structure:")
    print(df.head())

if __name__ == "__main__":
    #to create a sample CSV file
    create_csv()