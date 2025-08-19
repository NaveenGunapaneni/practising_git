#!/usr/bin/env python3
"""Test script for the new HTML format generation."""

import sys
from pathlib import Path
import pandas as pd

# Add the app directory to Python path
sys.path.append('.')

from app.modules.upload.processors.real_sentinel_hub_processor import RealSentinelHubProcessor


def create_test_data():
    """Create test data with the expected columns."""
    test_data = {
        'lp_no': ['LP001', 'LP002', 'LP003'],
        'extent_ac': [10.5, 15.2, 8.7],
        'POINT_ID': ['P001', 'P002', 'P003'],
        'EASTING-X': [123456, 123457, 123458],
        'NORTHING-Y': [987654, 987655, 987656],
        'LATITUDE': [12.345, 12.346, 12.347],
        'LONGITUDE': [78.901, 78.902, 78.903],
        'Before Period Start': ['2022-01-01', '2022-01-01', '2022-01-01'],
        'Before Period End': ['2022-12-31', '2022-12-31', '2022-12-31'],
        'After Period Start': ['2023-01-01', '2023-01-01', '2023-01-01'],
        'After Period End': ['2023-12-31', '2023-12-31', '2023-12-31'],
        'Vegetation (NDVI)-Before Value': [0.5, 0.6, 0.4],
        'Vegetation (NDVI)-After Value': [0.3, 0.7, 0.5],
        'Built-up Area (NDBI)-Before Value': [0.2, 0.1, 0.3],
        'Built-up Area (NDBI)-After Value': [0.4, 0.1, 0.2],
        'Water/Moisture (NDWI)-Before Value': [0.1, 0.2, 0.1],
        'Water/Moisture (NDWI)-After Value': [0.1, 0.1, 0.2],
        'Vegetation (NDVI)-Difference': [-0.2, 0.1, 0.1],
        'Vegetation (NDVI)-Interpretation': ['Vegetation decrease', 'Vegetation increase', 'No significant change'],
        'Vegetation (NDVI)-Significance': ['Yes', 'No', 'No'],
        'Built-up Area (NDBI)-Difference': [0.2, 0.0, -0.1],
        'Built-up Area (NDBI)-Interpretation': ['Built-up area increase', 'No significant change', 'Built-up area decrease'],
        'Built-up Area (NDBI)-Significance': ['Yes', 'No', 'No'],
        'Water/Moisture (NDWI)-Difference': [0.0, -0.1, 0.1],
        'Water/Moisture (NDWI)-Interpretation': ['No significant change', 'Water decrease', 'Water increase'],
        'Water/Moisture (NDWI)-Significance': ['No', 'Yes', 'No'],
        'Conversion_status': ['Successful', 'Successful', 'Successful']
    }
    
    return pd.DataFrame(test_data)


def test_new_html_format():
    """Test the new HTML format generation."""
    
    print("Testing new HTML format generation...")
    
    # Create test data
    df = create_test_data()
    print(f"Created test data with {len(df)} rows and {len(df.columns)} columns")
    
    # Test the column requirements method
    processor = RealSentinelHubProcessor()
    new_df = processor._apply_new_column_requirements(df)
    
    print(f"\nNew dataframe has {len(new_df)} rows and {len(new_df.columns)} columns")
    print("New columns:")
    for col in new_df.columns:
        print(f"  - {col}")
    
    # Check if the new "Field Visit Required" column is created correctly
    if 'Field Visit Required' in new_df.columns:
        print(f"\nField Visit Required values: {new_df['Field Visit Required'].tolist()}")
        
        # Verify the logic: should be "Yes" for rows where any significance is "Yes"
        expected_values = ['Yes', 'Yes', 'No']  # Row 1: NDVI Yes, Row 2: NDWI Yes, Row 3: All No
        actual_values = new_df['Field Visit Required'].tolist()
        
        if actual_values == expected_values:
            print("✅ Field Visit Required logic is correct!")
        else:
            print(f"❌ Field Visit Required logic is incorrect. Expected: {expected_values}, Got: {actual_values}")
    
    # Test HTML generation
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    html_path = output_dir / "test_new_format.html"
    processor._generate_new_html_output(df, html_path, "Test Engagement")
    
    if html_path.exists():
        print(f"✅ New HTML file generated successfully: {html_path}")
        
        # Check file size
        file_size = html_path.stat().st_size
        print(f"   File size: {file_size} bytes")
        
        # Read and check content
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'Field Visit Required' in content:
            print("✅ HTML contains 'Field Visit Required' column")
        else:
            print("❌ HTML missing 'Field Visit Required' column")
            
        if 'Greenary Result' in content:
            print("✅ HTML contains 'Greenary Result' column")
        else:
            print("❌ HTML missing 'Greenary Result' column")
            
        if 'Old Photo Period' in content:
            print("✅ HTML contains 'Old Photo Period' column")
        else:
            print("❌ HTML missing 'Old Photo Period' column")
            
        if 'New Photo Period' in content:
            print("✅ HTML contains 'New Photo Period' column")
        else:
            print("❌ HTML missing 'New Photo Period' column")
        
    else:
        print(f"❌ Failed to generate HTML file: {html_path}")
    
    print("\nTest completed!")


if __name__ == "__main__":
    test_new_html_format()
