"""
Employee data management service.
"""

import pandas as pd
import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging


class EmployeeService:
    """Service for managing employee data and birthday detection."""
    
    REQUIRED_COLUMNS = ['empid', 'first_name', 'second_name', 'email', 'dob', 'department']
    
    def __init__(self, csv_file: str):
        """Initialize employee service."""
        self.csv_file = Path(csv_file)
        self.logger = logging.getLogger(__name__)
        self._cached_df: Optional[pd.DataFrame] = None
        self._cache_timestamp: Optional[datetime.datetime] = None
    
    def load_employees(self, force_reload: bool = False) -> Optional[pd.DataFrame]:
        """
        Load employee data from CSV file with caching.
        
        Args:
            force_reload: Force reload even if cached data exists
            
        Returns:
            DataFrame with employee data or None if error
        """
        try:
            # Check if we need to reload
            if not force_reload and self._is_cache_valid():
                return self._cached_df
            
            self.logger.info(f"Loading employee data from {self.csv_file}")
            
            if not self.csv_file.exists():
                self.logger.error(f"CSV file not found: {self.csv_file}")
                return None
            
            # Load CSV
            df = pd.read_csv(self.csv_file)
            
            # Validate structure
            if not self._validate_csv_structure(df):
                return None
            
            # Process data
            df = self._process_employee_data(df)
            
            # Cache the result
            self._cached_df = df
            self._cache_timestamp = datetime.datetime.now()
            
            self.logger.info(f"Successfully loaded {len(df)} employees")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading employee data: {e}")
            return None
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid."""
        if self._cached_df is None or self._cache_timestamp is None:
            return False
        
        # Cache is valid for 1 hour or if file hasn't been modified
        cache_age = datetime.datetime.now() - self._cache_timestamp
        if cache_age.total_seconds() > 3600:  # 1 hour
            return False
        
        # Check if file was modified after cache
        file_mtime = datetime.datetime.fromtimestamp(self.csv_file.stat().st_mtime)
        return file_mtime <= self._cache_timestamp
    
    def _validate_csv_structure(self, df: pd.DataFrame) -> bool:
        """Validate that CSV has required columns."""
        missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            return False
        return True
    
    def _process_employee_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and clean employee data."""
        try:
            # Create full name
            df['full_name'] = df['first_name'].astype(str) + ' ' + df['second_name'].astype(str)
            
            # Parse birthdays with flexible format handling
            df['birthday'] = pd.to_datetime(df['dob'], format='mixed', dayfirst=True, errors='coerce')
            
            # Log any parsing issues
            invalid_dates = df[df['birthday'].isna()]
            if not invalid_dates.empty:
                self.logger.warning(f"Found {len(invalid_dates)} employees with invalid birth dates")
                for _, emp in invalid_dates.iterrows():
                    self.logger.warning(f"Invalid date for {emp['full_name']}: {emp['dob']}")
            
            # Remove employees with invalid dates
            df = df[df['birthday'].notna()].copy()
            
            # Clean email addresses
            df['email'] = df['email'].str.strip().str.lower()
            
            # Clean names
            df['first_name'] = df['first_name'].str.strip()
            df['second_name'] = df['second_name'].str.strip()
            df['full_name'] = df['full_name'].str.strip()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error processing employee data: {e}")
            raise
    
    def get_todays_birthdays(self, df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """
        Get employees who have birthdays today.
        
        Args:
            df: Employee DataFrame (loads if not provided)
            
        Returns:
            List of employee dictionaries
        """
        if df is None:
            df = self.load_employees()
            if df is None:
                return []
        
        today = datetime.date.today()
        birthday_employees = []
        
        for _, employee in df.iterrows():
            try:
                emp_birthday = employee['birthday'].date()
                if emp_birthday.month == today.month and emp_birthday.day == today.day:
                    birthday_employees.append(employee.to_dict())
            except Exception as e:
                self.logger.warning(f"Error checking birthday for {employee.get('full_name', 'Unknown')}: {e}")
                continue
        
        return birthday_employees
    
    def get_upcoming_birthdays(self, days_ahead: int = 7, df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """
        Get employees with birthdays in the next N days.
        
        Args:
            days_ahead: Number of days to look ahead
            df: Employee DataFrame (loads if not provided)
            
        Returns:
            List of employee dictionaries with birthday info
        """
        if df is None:
            df = self.load_employees()
            if df is None:
                return []
        
        today = datetime.date.today()
        upcoming_birthdays = []
        
        for _, employee in df.iterrows():
            try:
                emp_birthday = employee['birthday'].date()
                
                # Calculate this year's birthday
                this_year_birthday = emp_birthday.replace(year=today.year)
                
                # If birthday already passed this year, check next year
                if this_year_birthday < today:
                    this_year_birthday = emp_birthday.replace(year=today.year + 1)
                
                # Calculate days until birthday
                days_until = (this_year_birthday - today).days
                
                if 0 <= days_until <= days_ahead:
                    emp_dict = employee.to_dict()
                    emp_dict['days_until_birthday'] = days_until
                    emp_dict['birthday_this_year'] = this_year_birthday
                    upcoming_birthdays.append(emp_dict)
                    
            except Exception as e:
                self.logger.warning(f"Error checking upcoming birthday for {employee.get('full_name', 'Unknown')}: {e}")
                continue
        
        # Sort by days until birthday
        upcoming_birthdays.sort(key=lambda x: x['days_until_birthday'])
        return upcoming_birthdays
    
    def get_employee_by_id(self, empid: str, df: Optional[pd.DataFrame] = None) -> Optional[Dict[str, Any]]:
        """
        Get employee by ID.
        
        Args:
            empid: Employee ID
            df: Employee DataFrame (loads if not provided)
            
        Returns:
            Employee dictionary or None if not found
        """
        if df is None:
            df = self.load_employees()
            if df is None:
                return None
        
        employee_row = df[df['empid'] == empid]
        if employee_row.empty:
            return None
        
        return employee_row.iloc[0].to_dict()
    
    def get_employees_by_department(self, department: str, df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """
        Get all employees in a specific department.
        
        Args:
            department: Department name
            df: Employee DataFrame (loads if not provided)
            
        Returns:
            List of employee dictionaries
        """
        if df is None:
            df = self.load_employees()
            if df is None:
                return []
        
        dept_employees = df[df['department'].str.lower() == department.lower()]
        return [emp.to_dict() for _, emp in dept_employees.iterrows()]
    
    def validate_employee_email(self, email: str) -> bool:
        """
        Basic email validation.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email appears valid
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def get_statistics(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Get employee statistics.
        
        Args:
            df: Employee DataFrame (loads if not provided)
            
        Returns:
            Dictionary with statistics
        """
        if df is None:
            df = self.load_employees()
            if df is None:
                return {}
        
        today = datetime.date.today()
        stats = {
            'total_employees': len(df),
            'departments': df['department'].nunique(),
            'department_breakdown': df['department'].value_counts().to_dict(),
            'birthdays_today': len(self.get_todays_birthdays(df)),
            'upcoming_birthdays_week': len(self.get_upcoming_birthdays(7, df)),
            'invalid_emails': len(df[~df['email'].apply(self.validate_employee_email)]),
        }
        
        return stats


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test the service
    service = EmployeeService("employees.csv")
    
    # Load employees
    df = service.load_employees()
    if df is not None:
        print(f"Loaded {len(df)} employees")
        
        # Get today's birthdays
        birthdays = service.get_todays_birthdays(df)
        print(f"Today's birthdays: {len(birthdays)}")
        
        # Get statistics
        stats = service.get_statistics(df)
        print("Statistics:", stats)
    else:
        print("Failed to load employee data")