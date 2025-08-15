# Excel Formatting Guide - Environmental Analysis

## 🎯 Overview

The GeoPulse API now automatically converts CSV output files to professionally formatted Excel files with conditional formatting for environmental analysis data.

## 🚀 Features

### Automatic Processing
- **Integrated Workflow**: Excel formatting is automatically applied during file upload processing
- **Seamless Conversion**: CSV files are processed and converted to XLSX with formatting
- **No Additional Steps**: Users get formatted Excel files without extra requests

### Conditional Formatting Rules

| Column | Value | Background Color | Use Case |
|--------|-------|------------------|----------|
| **Vegetation (NDVI)-Significance** | "Yes" | 🔴 Red | Significant vegetation change detected |
| **Vegetation (NDVI)-Significance** | "No" | 🟢 Green | No significant vegetation change |
| **Built-up Area (NDBI)-Significance** | "Yes" | 🔴 Red | Significant construction/development |
| **Built-up Area (NDBI)-Significance** | "No" | 🟢 Green | No significant built-up change |
| **Water/Moisture (NDWI)-Significance** | "Yes" | 🔴 Red | Significant water/moisture change |
| **Water/Moisture (NDWI)-Significance** | "No" | 🟢 Green | No significant water change |

### Professional Styling
- **Header Row**: Blue background with white bold text
- **Data Alignment**: Numeric columns centered, text columns left-aligned
- **Borders**: Professional thin borders on all cells
- **Column Widths**: Auto-adjusted for optimal readability
- **Font**: Clean, readable fonts with appropriate sizing

## 📁 File Structure

### Before (CSV Only):
```
user_data/uploads/4/20250815_164217/
├── input/164217_land_area_demo.csv
└── output/20250815_164217_batch_analysis_before20250801_20250830.csv
```

### After (Automatic Excel):
```
user_data/uploads/4/20250815_164217/
├── input/164217_land_area_demo.csv
├── output/20250815_164217_batch_analysis_before20250801_20250830.csv
└── output/20250815_164217_batch_analysis_before20250801_20250830.xlsx  ← Formatted Excel
```

## 🔧 Usage

### 1. Automatic via API Upload

When you upload a file through the API, Excel formatting is applied automatically:

```bash
curl -X POST http://localhost:8000/api/v1/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@land_area_demo.csv" \
  -F "engagement_name=Environmental Analysis" \
  -F "date1=2025-08-01" \
  -F "date2=2025-08-15" \
  -F "date3=2025-08-30" \
  -F "date4=2025-09-15"
```

**Response includes Excel file path:**
```json
{
  "status": "success",
  "data": {
    "file_id": 4,
    "storage_location": "user_data/uploads/4/20250815_164217/output/analysis.xlsx",
    "processed_flag": true
  }
}
```

### 2. Manual Formatting with Standalone Utility

```bash
# Basic usage
python format_excel.py input_data.csv

# Specify output file
python format_excel.py input_data.csv formatted_output.xlsx

# Verbose output
python format_excel.py input_data.csv --verbose
```

### 3. Programmatic Usage

```python
from app.modules.upload.processors.excel_formatter import format_environmental_analysis_excel
from pathlib import Path

# Format a CSV file
csv_path = Path("data/analysis.csv")
excel_path = format_environmental_analysis_excel(csv_path)
print(f"Formatted Excel created: {excel_path}")
```

## 📊 Example Output

### Input CSV Data:
```csv
lp_no,extent_ac,Vegetation (NDVI)-Significance,Built-up Area (NDBI)-Significance,Water/Moisture (NDWI)-Significance
1,0.5,Yes,Yes,No
2,5.0,Yes,Yes,No
3,50.0,Yes,Yes,Yes
```

### Formatted Excel Result:
- **Header**: Blue background, white text, bold
- **Row 1**: Vegetation=🔴Red, Built-up=🔴Red, Water=🟢Green
- **Row 2**: Vegetation=🔴Red, Built-up=🔴Red, Water=🟢Green  
- **Row 3**: Vegetation=🔴Red, Built-up=🔴Red, Water=🔴Red

## 🎨 Color Scheme

### Background Colors:
- **Red (Significant)**: `#FFCCCC` - Light red for "Yes" values
- **Green (Not Significant)**: `#CCFFCC` - Light green for "No" values
- **Header Blue**: `#4472C4` - Professional blue for headers

### Text Colors:
- **Header Text**: White (`#FFFFFF`)
- **Data Text**: Black (default)

## 🔍 Technical Details

### Dependencies:
- `pandas` - Data manipulation
- `openpyxl` - Excel file creation and formatting
- `pathlib` - File path handling

### Performance:
- **Processing Time**: ~0.01-0.02 seconds for typical files
- **File Size**: Excel files are typically 2-3x larger than CSV
- **Memory Usage**: Minimal impact on system resources

### Error Handling:
- **Graceful Fallback**: If Excel formatting fails, CSV file is still provided
- **Logging**: Detailed logs for troubleshooting
- **Validation**: Input validation for file formats and data integrity

## 🚨 Troubleshooting

### Common Issues:

1. **Missing Significance Columns**
   ```
   Warning: Column 'Vegetation (NDVI)-Significance' not found
   ```
   **Solution**: Ensure your CSV has the expected column names

2. **Excel File Not Created**
   ```
   Error: Failed to create formatted Excel file
   ```
   **Solution**: Check file permissions and disk space

3. **Formatting Not Applied**
   ```
   Excel file created but no conditional formatting
   ```
   **Solution**: Verify significance column values are exactly "Yes" or "No"

### Debug Commands:

```bash
# Test standalone formatter
python format_excel.py your_file.csv --verbose

# Check API logs
tail -f logs/api.log | grep -i excel

# Verify file structure
ls -la user_data/uploads/*/*/output/
```

## 📈 Benefits

### For Users:
- **Professional Reports**: Ready-to-share Excel files with visual formatting
- **Quick Analysis**: Color-coded significance values for rapid assessment
- **No Manual Work**: Automatic formatting saves time and effort

### For Analysts:
- **Visual Clarity**: Immediate identification of significant changes
- **Consistent Format**: Standardized reporting across all analyses
- **Easy Sharing**: Professional Excel files for stakeholders

### For Developers:
- **Modular Design**: Reusable formatter component
- **Error Resilient**: Graceful handling of formatting failures
- **Extensible**: Easy to add new formatting rules

## 🔮 Future Enhancements

### Planned Features:
- **Charts and Graphs**: Automatic chart generation for trends
- **Summary Dashboard**: Executive summary sheet with key metrics
- **Custom Themes**: User-selectable color schemes
- **Advanced Filtering**: Excel filters and sorting capabilities
- **Data Validation**: Dropdown lists and input validation

### Configuration Options:
- **Color Customization**: User-defined colors for significance levels
- **Layout Options**: Different table layouts and styles
- **Export Formats**: Additional formats (PDF, PowerPoint)

## 📞 Support

For issues or questions about Excel formatting:

1. **Check Logs**: Review API logs for detailed error messages
2. **Test Standalone**: Use `format_excel.py` to isolate issues
3. **Verify Data**: Ensure CSV has expected column structure
4. **File Permissions**: Check read/write access to output directories

The Excel formatting feature enhances the GeoPulse API by providing professional, visually appealing reports that make environmental analysis results immediately actionable! 🌍📊