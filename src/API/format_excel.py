#!/usr/bin/env python3
"""
Standalone utility to format environmental analysis CSV files to Excel with conditional formatting.

Usage:
    python format_excel.py <csv_file_path>
    python format_excel.py <csv_file_path> <output_xlsx_path>

Features:
- Converts CSV to XLSX with professional formatting
- Applies conditional formatting to significance columns:
  * Vegetation (NDVI)-Significance: Yes=Red, No=Green
  * Built-up Area (NDBI)-Significance: Yes=Red, No=Green  
  * Water/Moisture (NDWI)-Significance: Yes=Red, No=Green
- Auto-adjusts column widths
- Adds professional styling with borders and colors
"""

import sys
import argparse
from pathlib import Path

# Add the app directory to Python path
sys.path.append('.')

from app.modules.upload.processors.excel_formatter import format_environmental_analysis_excel


def main():
    """Main function for the Excel formatter utility."""
    
    parser = argparse.ArgumentParser(
        description="Format environmental analysis CSV to Excel with conditional formatting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python format_excel.py data.csv
  python format_excel.py data.csv formatted_output.xlsx
  python format_excel.py user_data/uploads/4/20250815_164217/output/analysis.csv

Formatting Rules:
  - Significance columns with 'Yes' values: Red background
  - Significance columns with 'No' values: Green background
  - Header row: Blue background with white text
  - Auto-adjusted column widths for readability
        """
    )
    
    parser.add_argument(
        'csv_file',
        type=str,
        help='Path to the input CSV file'
    )
    
    parser.add_argument(
        'output_file',
        type=str,
        nargs='?',
        help='Path for the output XLSX file (optional, defaults to same name with .xlsx extension)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"❌ Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    if not csv_path.suffix.lower() == '.csv':
        print(f"❌ Error: Input file must be a CSV file: {csv_path}")
        sys.exit(1)
    
    # Determine output path
    if args.output_file:
        output_path = Path(args.output_file)
    else:
        output_path = csv_path.with_suffix('.xlsx')
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if args.verbose:
            print(f"📄 Input CSV: {csv_path}")
            print(f"📊 Output XLSX: {output_path}")
            print("🔄 Processing...")
        
        # Format the CSV to Excel
        result_path = format_environmental_analysis_excel(csv_path, output_path)
        
        print(f"✅ Successfully created formatted Excel file: {result_path}")
        
        if args.verbose:
            print("\n📋 Formatting applied:")
            print("   • Header row: Blue background with white text")
            print("   • Vegetation (NDVI)-Significance: 'Yes' = Red, 'No' = Green")
            print("   • Built-up Area (NDBI)-Significance: 'Yes' = Red, 'No' = Green")
            print("   • Water/Moisture (NDWI)-Significance: 'Yes' = Red, 'No' = Green")
            print("   • Auto-adjusted column widths")
            print("   • Professional borders and alignment")
            
            # Show file size
            file_size = result_path.stat().st_size
            if file_size > 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            elif file_size > 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size} bytes"
            
            print(f"   • File size: {size_str}")
        
    except Exception as e:
        print(f"❌ Error formatting Excel file: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()