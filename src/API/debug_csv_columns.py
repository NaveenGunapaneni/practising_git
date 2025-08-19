#!/usr/bin/env python3
"""Debug script to check CSV columns without authentication."""

import pandas as pd
from pathlib import Path
import sys

def debug_csv_columns():
    """Debug CSV columns in the user_data directory."""
    
    print("Debugging CSV columns...")
    
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
    
    # Try to read the CSV with different options
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    df = None
    
    for encoding in encodings:
        try:
            print(f"\nTrying encoding: {encoding}")
            df = pd.read_csv(
                latest_csv, 
                encoding=encoding,
                on_bad_lines='skip',
                engine='python',
                quoting=3
            )
            print(f"✅ Successfully read CSV with encoding: {encoding}")
            break
        except Exception as e:
            print(f"❌ Failed with encoding {encoding}: {str(e)}")
            continue
    
    if df is None:
        print("\n❌ Failed to read CSV with any encoding")
        return
    
    print(f"\n✅ CSV reading successful!")
    print(f"Shape: {df.shape}")
    print(f"Columns ({len(df.columns)}):")
    
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. '{col}' (type: {df[col].dtype})")
    
    print(f"\nFirst few rows:")
    print(df.head(2).to_string())
    
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
        for actual in df.columns:
            if expected.lower() in actual.lower():
                found = True
                found_columns.append(actual)
                print(f"  ✅ '{expected}' -> found as '{actual}'")
                break
        if not found:
            print(f"  ❌ '{expected}' -> NOT FOUND")
    
    print(f"\nFound {len(found_columns)} out of {len(expected_columns)} expected columns")
    
    # Show sample data for found columns
    if found_columns:
        print(f"\nSample data for found columns:")
        print(df[found_columns].head(2).to_string())


if __name__ == "__main__":
    debug_csv_columns()
