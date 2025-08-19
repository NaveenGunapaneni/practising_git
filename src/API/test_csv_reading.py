#!/usr/bin/env python3
"""Test script for CSV reading with problematic files."""

import pandas as pd
from pathlib import Path

def test_csv_reading():
    """Test CSV reading with different options."""
    
    print("Testing CSV reading with problematic files...")
    
    # Look for CSV files in the user_data directory
    csv_files = list(Path("user_data/uploads").rglob("*.csv"))
    
    if not csv_files:
        print("No CSV files found in user_data/uploads")
        return
    
    # Sort by modification time and get the most recent
    csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_csv = csv_files[0]
    
    print(f"Testing with file: {latest_csv}")
    
    # Try different encodings and CSV parsing options
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    df = None
    
    for encoding in encodings:
        try:
            print(f"Trying encoding: {encoding}")
            df = pd.read_csv(
                latest_csv, 
                encoding=encoding,
                on_bad_lines='skip',
                engine='python',
                quoting=3
            )
            print(f"✅ Successfully read CSV with encoding: {encoding}")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            break
        except (UnicodeDecodeError, pd.errors.ParserError) as e:
            print(f"❌ Failed with encoding {encoding}: {str(e)}")
            continue
    
    # If still failed, try with more aggressive error handling
    if df is None:
        print("\nTrying fallback options...")
        for encoding in encodings:
            try:
                df = pd.read_csv(
                    latest_csv, 
                    encoding=encoding,
                    on_bad_lines='skip',
                    engine='python',
                    quoting=3,
                    sep=None,
                    error_bad_lines=False,
                    warn_bad_lines=False
                )
                print(f"✅ Successfully read CSV with fallback options and encoding: {encoding}")
                print(f"   Shape: {df.shape}")
                print(f"   Columns: {list(df.columns)}")
                break
            except Exception as e:
                print(f"❌ Failed with fallback options and encoding {encoding}: {str(e)}")
                continue
    
    if df is not None:
        print(f"\n✅ CSV reading successful!")
        print(f"Final shape: {df.shape}")
        print(f"First few columns: {list(df.columns)[:10]}")
        
        # Check for expected columns
        expected_columns = [
            'lp_no', 'extent_ac', 'POINT_ID', 'EASTING-X', 'NORTHING-Y', 
            'LATITUDE', 'LONGITUDE', 'Before Period Start', 'After Period Start'
        ]
        
        print(f"\nChecking for expected columns:")
        for col in expected_columns:
            if col in df.columns:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} (missing)")
    else:
        print("❌ Failed to read CSV with any method")


if __name__ == "__main__":
    test_csv_reading()
