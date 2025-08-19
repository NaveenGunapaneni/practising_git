#!/usr/bin/env python3
"""Test script to verify column transformation works correctly."""

import pandas as pd
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append('.')

def create_test_data():
    """Create test data similar to the working HTML file."""
    test_data = {
        'lp_no': [2, 2, 3],
        'extent_ac': [206.49, 206.49, 0.0],
        'POINT_ID': [1, 2, 3],
        'EASTING-X': [340751.55, 340869.12, 0.0],
        'NORTHING-Y': [1590485.86, 1590228.96, 0.0],
        'LATITUDE': [14.382015, 14.379700, 0.0],
        'LONGITUDE': [79.523023, 79.524128, 0.0],
        'Before Period Start': ['2025-01-01', '2025-01-01', '2025-01-01'],
        'Before Period End': ['2025-03-31', '2025-03-31', '2025-03-31'],
        'After Period Start': ['2025-07-01', '2025-07-01', '2025-07-01'],
        'After Period End': ['2025-07-31', '2025-07-31', '2025-07-31'],
        'Vegetation (NDVI)-Before Value': [0.5, 0.6, 0.4],
        'Vegetation (NDVI)-After Value': [0.7, 0.8, 0.5],
        'Built-up Area (NDBI)-Before Value': [0.2, 0.1, 0.3],
        'Built-up Area (NDBI)-After Value': [0.4, 0.3, 0.2],
        'Water/Moisture (NDWI)-Before Value': [0.1, 0.2, 0.1],
        'Water/Moisture (NDWI)-After Value': [0.1, 0.1, 0.2],
        'Vegetation (NDVI)-Difference': [0.2, 0.2, 0.1],
        'Vegetation (NDVI)-Interpretation': ['Vegetation growth or improvement', 'Vegetation growth or improvement', ''],
        'Vegetation (NDVI)-Significance': ['Yes', 'Yes', 'No'],
        'Built-up Area (NDBI)-Difference': [0.2, 0.2, -0.1],
        'Built-up Area (NDBI)-Interpretation': ['Construction or development increase', 'Construction or development increase', ''],
        'Built-up Area (NDBI)-Significance': ['Yes', 'Yes', 'No'],
        'Water/Moisture (NDWI)-Difference': [0.0, -0.1, 0.1],
        'Water/Moisture (NDWI)-Interpretation': ['No significant water change', 'No significant water change', ''],
        'Water/Moisture (NDWI)-Significance': ['No', 'No', 'No'],
        'Conversion_status': ['Successful', 'Successful', 'Successful']
    }
    
    return pd.DataFrame(test_data)

def test_column_transformation():
    """Test the column transformation logic."""
    
    print("Testing column transformation...")
    
    # Create test data
    df = create_test_data()
    print(f"Original dataframe shape: {df.shape}")
    print(f"Original columns: {list(df.columns)}")
    
    # Import the transformation function
    try:
        from app.modules.upload.processors.real_sentinel_hub_processor import RealSentinelHubProcessor
        processor = RealSentinelHubProcessor()
        
        # Apply transformation
        new_df = processor._apply_new_column_requirements(df)
        
        print(f"\nTransformed dataframe shape: {new_df.shape}")
        print(f"Transformed columns: {list(new_df.columns)}")
        
        # Check expected columns
        expected_columns = [
            'lp_no', 'extent_ac', 'POINT_ID', 'EASTING-X', 'NORTHING-Y', 
            'LATITUDE', 'LONGITUDE', 'Old Photo Period', 'New Photo Period',
            'Greenary Result', 'Construction Result', 'Water/Moisture Result',
            'Field Visit Required'
        ]
        
        print(f"\nChecking expected columns:")
        for col in expected_columns:
            if col in new_df.columns:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} (missing)")
        
        # Show sample data
        print(f"\nSample data:")
        print(new_df.head(2).to_string())
        
        return new_df
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_column_transformation()
