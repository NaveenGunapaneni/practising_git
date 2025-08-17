# GeoPulse User Documentation

Welcome to GeoPulse! This comprehensive guide will walk you through every aspect of using the GeoPulse application, from registration to interpreting your results.

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Registration](#user-registration)
3. [User Login](#user-login)
4. [Dashboard Overview](#dashboard-overview)
5. [File Upload Process](#file-upload-process)
6. [Understanding Your Results](#understanding-your-results)
7. [Dashboard Interpretation](#dashboard-interpretation)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Getting Started

### What is GeoPulse?
GeoPulse is a property analysis tool that helps you understand how properties and their surroundings have changed over time. It uses satellite images to show you what has changed in terms of vegetation, water, and development around your properties.

### System Requirements
- **Browser**: Any modern web browser (Chrome, Firefox, Safari, Edge)
- **Internet**: Stable internet connection
- **File Format**: CSV files only
- **File Size**: Maximum 50MB per file

### Supported File Format
- **CSV** (.csv) - Comma-separated values file

---

## User Registration

### Step 1: Access the Registration Page
1. Open your web browser
2. Navigate to the GeoPulse application URL
3. You'll see the GeoPulse login screen with the official logo
4. Click on the **"Register"** button or link

![GeoPulse Login Screen](../UI/public/images/AP_logo2.avif)
*GeoPulse Application Login Screen*

### Step 2: Fill in Registration Form
Complete the registration form with the following information:

| Field | Description | Requirements |
|-------|-------------|--------------|
| **Organization Name** | Your company or organization name | Required, 2-255 characters |
| **User Name** | Your full name | Required, 2-255 characters |
| **Contact Phone** | Your phone number | Required, valid phone format |
| **Email Address** | Your email address | Required, valid email format, unique |
| **Password** | Your account password | Required, minimum 8 characters with mix of letters, numbers, and symbols |

### Step 3: Submit Registration
1. Review all information for accuracy
2. Check the terms and conditions box (if applicable)
3. Click **"Register"** button

### Registration Success
Upon successful registration, you will:
- Receive a confirmation message
- Be automatically logged in
- Be redirected to the dashboard
- Receive 50 free property analyses

### Registration Troubleshooting

| Issue | Solution |
|-------|----------|
| **Email already exists** | Use a different email address or try logging in |
| **Password too weak** | Ensure password meets all requirements |
| **Invalid phone number** | Use standard format: +1-555-123-4567 |
| **Organization name too short** | Use at least 2 characters |

---

## User Login

### Step 1: Access Login Page
1. Navigate to the GeoPulse application
2. You'll see the login screen with the official logo
3. Click **"Login"** button or link
4. You'll be redirected to the login page

![GeoPulse Login Screen](../UI/public/images/AP_logo2.avif)
*GeoPulse Application Login Screen*

### Step 2: Enter Credentials
Provide your login information:

| Field | Description |
|-------|-------------|
| **Email Address** | The email you used during registration |
| **Password** | Your account password |

### Step 3: Login
1. Double-check your credentials
2. Click **"Login"** button
3. You'll be redirected to your dashboard

### Login Troubleshooting

| Issue | Solution |
|-------|----------|
| **Invalid email/password** | Check spelling and ensure caps lock is off |
| **Account locked** | Contact support if multiple failed attempts |
| **Forgot password** | Use "Forgot Password" link (if available) |
| **Account expired** | Contact support to reactivate your account |

### Session Management
- **Session Duration**: 30 minutes of inactivity
- **Auto-logout**: You'll be logged out after 30 minutes
- **Remember Me**: Option to stay logged in (if available)

---

## Dashboard Overview

### Dashboard Layout
The dashboard is your central hub for managing your GeoPulse account and data.

![GeoPulse Dashboard](../UI/public/images/AP_logo2.avif)
*GeoPulse Application Dashboard*

#### Header Section
- **Logo**: GeoPulse branding
- **Navigation Menu**: Access to different sections
- **User Profile**: Your name and account options
- **Logout**: Secure logout option

#### Main Dashboard Components

##### 1. Account Summary
```
Organization: [Your Organization Name]
User: [Your Name]
Email: [your.email@example.com]
Account Status: Active
Analyses Remaining: [X] / 50
Account Expires: [Date]
```

##### 2. File Management
- **Total Files**: Number of files uploaded
- **Processed Files**: Files that have been analyzed
- **Pending Files**: Files waiting for processing
- **Failed Files**: Files that encountered errors

##### 3. Recent Activity
- **Last Upload**: Date and time of your most recent file
- **Last Processing**: When your last file was analyzed
- **System Status**: Current processing queue status

##### 4. Quick Actions
- **Upload New File**: Direct link to file upload
- **View All Files**: Access to file management
- **Download Results**: Access to processed data
- **Account Settings**: Manage your profile

---

## File Upload Process

### Step 1: Prepare Your Data File

#### Required File Format
Your data file must contain the following columns:

| Column Name | Description | Required | Format |
|-------------|-------------|----------|--------|
| **property_id** | Unique identifier for each property | Yes | Text/Number |
| **address** | Property address | Yes | Text |
| **city** | City name | Yes | Text |
| **state** | State or province | Yes | Text |
| **zip_code** | Postal/ZIP code | Yes | Text/Number |
| **latitude** | Property latitude (optional) | No | Number |
| **longitude** | Property longitude (optional) | No | Number |

#### Sample Data Format
```csv
property_id,address,city,state,zip_code,latitude,longitude
1,123 Main St,New York,NY,10001,40.7128,-74.0060
2,456 Oak Ave,Los Angeles,CA,90210,34.0522,-118.2437
3,789 Pine Rd,Chicago,IL,60601,41.8781,-87.6298
```

### Step 2: Upload Your File

#### Method 1: Drag and Drop
1. Open the **Upload** page
2. Drag your file from your computer to the upload area
3. Drop the file in the designated zone
4. The file will automatically upload

#### Method 2: Browse and Select
1. Click **"Choose File"** or **"Browse"** button
2. Navigate to your file location
3. Select the file
4. Click **"Open"**
5. Click **"Upload"** button

### Step 3: File Validation
The system will automatically validate your file:

#### Validation Checks
- **File Format**: Ensures file is CSV format
- **File Size**: Confirms file is under 50MB
- **Required Columns**: Verifies all required columns are present
- **Data Quality**: Checks for basic data completeness

#### Validation Results
```
✅ File format: CSV
✅ File size: 2.5MB (under 50MB limit)
✅ Required columns: All present
✅ Data quality: Good
📊 Properties found: 1,250
⏱️ Estimated processing time: 15 minutes
```

### Step 4: Processing Confirmation
After successful upload:
- **File Status**: "Uploaded - Processing"
- **Processing Queue**: Your file joins the processing queue
- **Estimated Time**: System provides processing time estimate
- **API Calls**: System calculates required API calls

#### Processing Information
```
File: properties_data.csv
Properties: 1,250
Required Analyses: 2,500 (2 analyses per property)
Your Remaining Analyses: 50
Status: Insufficient analyses
Action: Contact support to purchase additional analyses
```

---

## Understanding Your Results

### Processing Stages

#### Stage 1: Data Check
- **File Check**: Verifies your file format and data
- **Address Processing**: Converts addresses to map locations (if needed)
- **Quality Review**: Checks data accuracy

#### Stage 2: Satellite Image Collection
- **Before Images**: Collects satellite photos from the "before" period
- **After Images**: Collects satellite photos from the "after" period
- **Image Processing**: Analyzes the differences between periods

#### Stage 3: Analysis and Report Creation
- **Change Detection**: Identifies what has changed
- **Calculation**: Measures the amount of change
- **Report Creation**: Creates your analysis report

### Output Files

#### 1. Main Analysis Report (CSV)
Contains detailed analysis for each property:

| Column | Description |
|--------|-------------|
| **property_id** | Original property identifier |
| **address** | Property address |
| **before_period** | Analysis period (before) |
| **after_period** | Analysis period (after) |
| **vegetation_change** | Vegetation change percentage |
| **water_change** | Water body change percentage |
| **urban_change** | Urban development change percentage |
| **confidence_score** | Analysis confidence (0-100) |
| **processing_status** | Success/Error status |
| **error_message** | Error details (if any) |

#### 2. Summary Report
High-level statistics and insights showing:
- Total number of properties analyzed
- How many were successfully processed
- Average changes in vegetation, water, and development
- Breakdown of change categories
- Processing time and date

#### 3. Visual Reports
- **Maps**: Interactive maps showing your properties and changes
- **Charts**: Easy-to-read graphs showing change patterns
- **Visual Summaries**: Color-coded maps showing change intensity

### Understanding Change Metrics

#### Vegetation Change
- **Positive Values**: Increase in vegetation (reforestation, growth)
- **Negative Values**: Decrease in vegetation (deforestation, development)
- **Range**: Typically -100% to +100%
- **Interpretation**: 
  - -50% to -100%: Significant vegetation loss
  - -10% to -50%: Moderate vegetation loss
  - -10% to +10%: Minimal change
  - +10% to +50%: Moderate vegetation gain
  - +50% to +100%: Significant vegetation gain

#### Water Change
- **Positive Values**: Increase in water bodies (flooding, new water features)
- **Negative Values**: Decrease in water bodies (drying, drainage)
- **Range**: Typically -100% to +100%
- **Interpretation**:
  - -50% to -100%: Significant water loss
  - -10% to -50%: Moderate water loss
  - -10% to +10%: Minimal change
  - +10% to +50%: Moderate water gain
  - +50% to +100%: Significant water gain

#### Urban Change
- **Positive Values**: Increase in urban development
- **Negative Values**: Decrease in urban development (rare)
- **Range**: Typically 0% to +100%
- **Interpretation**:
  - 0% to 10%: Minimal development
  - 10% to 30%: Moderate development
  - 30% to 60%: Significant development
  - 60% to 100%: Major development

#### Confidence Score
- **90-100**: High confidence in analysis
- **70-89**: Good confidence in analysis
- **50-69**: Moderate confidence in analysis
- **30-49**: Low confidence in analysis
- **0-29**: Very low confidence, results may be unreliable

---

## Dashboard Interpretation

### File Management Dashboard

#### File Status Indicators
```
📁 Uploaded Files
├── 🟢 Processed (Success)
├── 🟡 Processing (In Progress)
├── 🔴 Failed (Error)
└── ⚪ Pending (Waiting)
```

#### File Details View
Click on any file to see detailed information:

```
File: properties_analysis_2024.csv
Upload Date: January 15, 2024, 10:30 AM
File Size: 2.5 MB
Properties: 1,250
Status: ✅ Completed
Processing Time: 1h 15m
API Calls Used: 2,400
Results: Available for download
```

### Results Dashboard

#### Summary Statistics
```
📊 Analysis Summary
├── Total Properties: 1,250
├── Successfully Processed: 1,200 (96%)
├── Failed Processing: 50 (4%)
├── Average Processing Time: 45 seconds per property
└── Total API Calls Used: 2,400
```

#### Change Analysis Overview
```
🌱 Vegetation Changes
├── Significant Decrease: 150 properties (12%)
├── Moderate Decrease: 300 properties (24%)
├── No Change: 500 properties (40%)
├── Moderate Increase: 250 properties (20%)
└── Significant Increase: 50 properties (4%)

💧 Water Changes
├── Significant Decrease: 25 properties (2%)
├── Moderate Decrease: 100 properties (8%)
├── No Change: 1,000 properties (80%)
├── Moderate Increase: 100 properties (8%)
└── Significant Increase: 25 properties (2%)

🏗️ Urban Development
├── No Development: 800 properties (64%)
├── Minimal Development: 300 properties (24%)
├── Moderate Development: 100 properties (8%)
└── Significant Development: 50 properties (4%)
```

### Interactive Features

#### 1. Filtering and Sorting
- **Filter by Change Type**: View only properties with specific changes
- **Filter by Confidence**: Show only high-confidence results
- **Sort by Change Magnitude**: Order by most significant changes
- **Search by Address**: Find specific properties

#### 2. Export Options
- **Download CSV**: Full analysis results
- **Download JSON**: Summary statistics
- **Download Maps**: Visual representations
- **Download Report**: Comprehensive PDF report

#### 3. Visualization Tools
- **Interactive Maps**: Click on properties to see details
- **Change Charts**: Visual representation of change distributions
- **Time Series**: View changes over time (if multiple analyses)
- **Comparison Tools**: Compare different analysis periods

### Key Metrics to Monitor

#### 1. Processing Success Rate
- **Target**: >95% successful processing
- **Action if Low**: Check data quality and file format

#### 2. Average Confidence Score
- **Target**: >70% average confidence
- **Action if Low**: Review data quality and coordinate accuracy

#### 3. Change Distribution
- **Expected**: Most properties show minimal change (-10% to +10%)
- **Action if Unusual**: Investigate data quality or environmental events

#### 4. Analysis Efficiency
- **Target**: 2 analyses per property (before + after comparison)
- **Action if High**: Check for duplicate processing or errors

---

## Troubleshooting

### Common Issues and Solutions

#### File Upload Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **File too large** | File exceeds 50MB limit | Compress file or split into smaller files |
| **Invalid file format** | File not CSV format | Convert file to CSV format |
| **Missing required columns** | Required columns not present | Add missing columns to your file |
| **Upload timeout** | Slow internet connection | Try uploading during off-peak hours |

#### Processing Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **Low confidence scores** | Poor address quality | Improve address accuracy and completeness |
| **High failure rate** | Invalid coordinates | Verify latitude/longitude data |
| **Processing delays** | High system load | Wait for processing to complete |
| **Insufficient analyses** | Exceeded analysis limit | Purchase additional analyses |

#### Account Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **Cannot login** | Wrong credentials | Reset password or contact support |
| **Account expired** | 30-day trial expired | Contact support to extend or upgrade |
| **Analyses depleted** | Used all allocated analyses | Purchase additional analyses |
| **Session timeout** | Inactive for 30 minutes | Log in again |

### Getting Help

#### Support Channels
- **Email Support**: support@geopulse.com
- **Phone Support**: +1-555-123-4567
- **Live Chat**: Available during business hours
- **Documentation**: This user guide and online help

#### Information to Provide
When contacting support, please provide:
- **Account Email**: Your registered email address
- **File Name**: Name of the file you're working with
- **Error Message**: Exact error message received
- **Steps Taken**: What you were doing when the error occurred
- **Screenshot**: Visual evidence of the issue (if applicable)

---

## FAQ

### General Questions

**Q: How much does GeoPulse cost?**
A: GeoPulse offers a free trial with 50 property analyses. Additional analyses can be purchased based on your needs.

**Q: How long does processing take?**
A: Processing time depends on the number of properties. Typically, 1,000 properties take 15-30 minutes.

**Q: Can I upload multiple files?**
A: Yes, you can upload multiple files. Each file is processed independently.

**Q: What happens if my file fails to process?**
A: Failed files are marked with error details. You can review the errors and re-upload corrected files.

### Technical Questions

**Q: What map system does GeoPulse use?**
A: GeoPulse uses standard latitude and longitude coordinates that work with most mapping systems.

**Q: How accurate are the satellite analyses?**
A: Accuracy depends on the quality of your data and weather conditions. The confidence score tells you how reliable the results are.

**Q: Can I analyze historical data?**
A: Yes, GeoPulse can analyze changes between different time periods using available satellite images.

**Q: What satellite images are used?**
A: GeoPulse uses multiple satellite sources to provide comprehensive analysis of your properties.

### Data Questions

**Q: How do I interpret negative vegetation change?**
A: Negative values indicate vegetation loss, which could be due to development, deforestation, or seasonal changes.

**Q: What does a high confidence score mean?**
A: High confidence (90-100%) means the analysis is very reliable. Low confidence suggests potential data quality issues.

**Q: Can I export my results?**
A: Yes, you can download results in CSV, JSON, and PDF formats.

**Q: How long are my results stored?**
A: Results are stored for 12 months from the processing date.

### Account Questions

**Q: How do I reset my password?**
A: Use the "Forgot Password" link on the login page or contact support.

**Q: Can I share my account with others?**
A: Accounts are for individual use. Contact support for team or enterprise solutions.

**Q: How do I purchase additional analyses?**
A: Contact support or use the "Purchase Credits" option in your dashboard.

**Q: What happens when my account expires?**
A: You'll need to contact support to extend your account or upgrade to a paid plan.

---

## Conclusion

This user documentation provides comprehensive guidance for using GeoPulse effectively. Remember:

1. **Start Small**: Begin with a small dataset to understand the process
2. **Check Data Quality**: Ensure your input data is accurate and complete
3. **Monitor Processing**: Keep track of your file processing status
4. **Review Results**: Carefully examine confidence scores and change metrics
5. **Contact Support**: Don't hesitate to reach out if you need help

For the most up-to-date information and additional resources, visit our online documentation portal or contact our support team.

---

*Last Updated: January 2024*
*Version: 1.0*
