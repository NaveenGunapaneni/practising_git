"""Test Data Generator for Integration Tests."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker
import random
from config import TEST_DATA_DIR, SAMPLE_FILES

fake = Faker()

class TestDataGenerator:
    """Generate test data for integration testing."""
    
    def __init__(self):
        """Initialize the test data generator."""
        self.test_data_dir = TEST_DATA_DIR
        self.test_data_dir.mkdir(exist_ok=True)
    
    def generate_valid_xlsx(self, filename: str = "sample_valid.xlsx", rows: int = 100):
        """Generate a valid Excel file with geospatial data."""
        # Generate sample geospatial data
        data = []
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(rows):
            # Generate coordinates within a reasonable range
            latitude = random.uniform(12.9716, 13.0827)  # Bangalore area
            longitude = random.uniform(77.5946, 77.6413)
            
            # Generate date
            date = base_date + timedelta(days=random.randint(0, 365))
            
            # Generate some environmental values
            temperature = random.uniform(20, 35)
            humidity = random.uniform(40, 90)
            rainfall = random.uniform(0, 50)
            
            data.append({
                'latitude': round(latitude, 6),
                'longitude': round(longitude, 6),
                'date': date.strftime('%Y-%m-%d'),
                'temperature': round(temperature, 2),
                'humidity': round(humidity, 2),
                'rainfall': round(rainfall, 2),
                'location': fake.city(),
                'station_id': f"ST{fake.random_number(digits=4)}",
                'value': round(random.uniform(0, 100), 2)
            })
        
        df = pd.DataFrame(data)
        file_path = self.test_data_dir / filename
        df.to_excel(file_path, index=False)
        return file_path
    
    def generate_valid_csv(self, filename: str = "sample_valid.csv", rows: int = 50):
        """Generate a valid CSV file with geospatial data."""
        data = []
        base_date = datetime.now() - timedelta(days=180)
        
        for i in range(rows):
            latitude = random.uniform(12.9716, 13.0827)
            longitude = random.uniform(77.5946, 77.6413)
            date = base_date + timedelta(days=random.randint(0, 180))
            
            data.append({
                'latitude': round(latitude, 6),
                'longitude': round(longitude, 6),
                'date': date.strftime('%Y-%m-%d'),
                'value': round(random.uniform(0, 100), 2),
                'category': random.choice(['A', 'B', 'C']),
                'description': fake.sentence()
            })
        
        df = pd.DataFrame(data)
        file_path = self.test_data_dir / filename
        df.to_csv(file_path, index=False)
        return file_path
    
    def generate_invalid_format(self, filename: str = "sample_invalid.txt"):
        """Generate an invalid format file."""
        file_path = self.test_data_dir / filename
        with open(file_path, 'w') as f:
            f.write("This is not a valid data file.\n")
            f.write("It contains plain text instead of structured data.\n")
            f.write("This should be rejected by the application.\n")
        return file_path
    
    def generate_large_file(self, filename: str = "sample_large.xlsx", rows: int = 10000):
        """Generate a large Excel file to test file size limits."""
        return self.generate_valid_xlsx(filename, rows)
    
    def generate_malformed_data(self, filename: str = "sample_malformed.xlsx"):
        """Generate a file with malformed data (missing required columns)."""
        data = []
        for i in range(20):
            data.append({
                'name': fake.name(),
                'email': fake.email(),
                'phone': fake.phone_number(),
                # Missing required columns: latitude, longitude, date, value
            })
        
        df = pd.DataFrame(data)
        file_path = self.test_data_dir / filename
        df.to_excel(file_path, index=False)
        return file_path
    
    def generate_test_user_data(self):
        """Generate test user data."""
        return {
            "organization_name": fake.company(),
            "user_name": fake.name(),
            "contact_phone": fake.phone_number(),
            "email": fake.email(),
            "password": fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
        }
    
    def generate_all_test_data(self):
        """Generate all test data files."""
        print("🔄 Generating test data files...")
        
        files = {}
        
        # Generate valid files
        files['valid_xlsx'] = self.generate_valid_xlsx()
        files['valid_csv'] = self.generate_valid_csv()
        
        # Generate invalid files
        files['invalid_format'] = self.generate_invalid_format()
        files['malformed_data'] = self.generate_malformed_data()
        
        # Generate large file
        files['large_file'] = self.generate_large_file(rows=1000)  # Smaller for testing
        
        print("✅ Test data files generated successfully!")
        for file_type, file_path in files.items():
            print(f"   📄 {file_type}: {file_path}")
        
        return files
    
    def cleanup_test_data(self):
        """Clean up all test data files."""
        print("🧹 Cleaning up test data files...")
        for file_path in self.test_data_dir.glob("*"):
            if file_path.is_file():
                file_path.unlink()
        print("✅ Test data cleanup completed!")


if __name__ == "__main__":
    # Generate test data when run directly
    generator = TestDataGenerator()
    generator.generate_all_test_data()
