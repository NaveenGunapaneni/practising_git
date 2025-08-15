#!/usr/bin/env python3
"""Test script for Excel formatter with environmental analysis data."""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append('.')

from app.modules.upload.processors.excel_formatter import format_environmental_analysis_excel


def test_excel_formatting():
    """Test the Excel formatter with actual data."""
    
    # Find the most recent CSV output file
    csv_files = list(Path("user_data/uploads").rglob("*.csv"))
    
    if not csv_files:
        print("No CSV files found in user_data/uploads")
        return
    
    # Sort by modification time and get the most recent
    csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_csv = csv_files[0]
    
    print(f"Found CSV file: {latest_csv}")
    
    try:
        # Format the CSV to Excel
        output_xlsx = format_environmental_analysis_excel(latest_csv)
        
        print(f"✅ Successfully created formatted Excel file: {output_xlsx}")
        print("\nFormatting applied:")
        print("- Header row: Blue background with white text")
        print("- Vegetation (NDVI)-Significance: 'Yes' = Red, 'No' = Green")
        print("- Built-up Area (NDBI)-Significance: 'Yes' = Red, 'No' = Green") 
        print("- Water/Moisture (NDWI)-Significance: 'Yes' = Red, 'No' = Green")
        print("- Auto-adjusted column widths")
        print("- Professional borders and alignment")
        
        return output_xlsx
        
    except Exception as e:
        print(f"❌ Error formatting Excel file: {str(e)}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use provided CSV file path
        csv_path = Path(sys.argv[1])
        if csv_path.exists():
            try:
                output_xlsx = format_environmental_analysis_excel(csv_path)
                print(f"✅ Formatted Excel file created: {output_xlsx}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        else:
            print(f"❌ CSV file not found: {csv_path}")
    else:
        # Test with latest file
        test_excel_formatting()