#!/usr/bin/env python3
"""Simple CSV debug script without pandas dependency."""

import csv
from pathlib import Path

def debug_csv_simple():
    """Debug CSV columns using built-in csv module."""
    
    print("Debugging CSV columns with simple approach...")
    
    # Look for CSV files in the user_data directory
    csv_files = list(Path("user_data/uploads").rglob("*.csv"))
    
    if not csv_files:
        print("No CSV files found in user_data/uploads")
        return
    
    # Sort by modification time and get the most recent
    csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_csv = csv_files[0]
    
    print(f"Analyzing file: {latest_csv}")
    print(f"File size: {latest_csv.stat().st_size} bytes")
    
    # Try to read the CSV with different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            print(f"\nTrying encoding: {encoding}")
            
            with open(latest_csv, 'r', encoding=encoding, newline='') as file:
                # Read first few lines to check structure
                reader = csv.reader(file)
                
                # Read header
                header = next(reader)
                print(f"✅ Successfully read CSV with encoding: {encoding}")
                print(f"Header row has {len(header)} columns")
                print(f"Columns:")
                
                for i, col in enumerate(header, 1):
                    print(f"  {i:2d}. '{col}'")
                
                # Read first few data rows
                print(f"\nFirst 2 data rows:")
                for row_num in range(2):
                    try:
                        row = next(reader)
                        print(f"  Row {row_num + 1}: {row[:5]}...")  # Show first 5 values
                    except StopIteration:
                        break
                
                break
                
        except UnicodeDecodeError as e:
            print(f"❌ Failed with encoding {encoding}: {str(e)}")
            continue
        except Exception as e:
            print(f"❌ Failed with encoding {encoding}: {str(e)}")
            continue
    
    # Check for expected columns
    print(f"\nChecking for expected columns:")
    expected_columns = [
        'lp_no', 'extent_ac', 'POINT_ID', 'EASTING-X', 'NORTHING-Y', 
        'LATITUDE', 'LONGITUDE', 'Before Period Start', 'After Period Start',
        'Vegetation (NDVI)-Interpretation', 'Built-up Area (NDBI)-Interpretation',
        'Water/Moisture (NDWI)-Interpretation'
    ]
    
    found_columns = []
    for expected in expected_columns:
        found = False
        for actual in header:
            if expected.lower() in actual.lower():
                found = True
                found_columns.append(actual)
                print(f"  ✅ '{expected}' -> found as '{actual}'")
                break
        if not found:
            print(f"  ❌ '{expected}' -> NOT FOUND")
    
    print(f"\nFound {len(found_columns)} out of {len(expected_columns)} expected columns")


if __name__ == "__main__":
    debug_csv_simple()
