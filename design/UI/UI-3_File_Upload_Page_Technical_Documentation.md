# UI-3: File Upload Page - Technical Documentation
## GeoPulse Web Application

**Component:** File Upload Page  
**Date:** August 2025  
**Version:** 1.0  
**Framework:** React.js 18.x  

---

## Table of Contents
1. [Wireframe Diagrams](#wireframe-diagrams)
2. [Test API Setup](#test-api-setup)
3. [Testing Tips](#testing-tips)
4. [UX Styling Guidelines](#ux-styling-guidelines)

---

## Wireframe Diagrams

### Desktop Layout (1200px+)
```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo] GeoPulse                    [User Name] [Avatar] [Logout]│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│              ┌─────────────────────────────────┐              │
│              │                                 │              │
│              │        Upload New File         │              │
│              │                                 │              │
│              │  ┌─────────────────────────────┐ │              │
│              │  │ Drag & Drop Area            │ │              │
│              │  │                             │ │              │
│              │  │    📁 Drop files here or    │ │              │
│              │  │    [Browse Files] button    │ │              │
│              │  │                             │ │              │
│              │  │    Supported: .xlsx, .csv   │ │              │
│              │  │    Max size: 50MB           │ │              │
│              │  └─────────────────────────────┘ │              │
│              │                                 │              │
│              │  ┌─────────────────────────────┐ │              │
│              │  │ Engagement Name             │ │              │
│              │  │ [________________________] │ │              │
│              │  │                             │ │              │
│              │  │ Date 1 (YYYY-MM-DD)         │ │              │
│              │  │ [2025-01-15]                │ │              │
│              │  │                             │ │              │
│              │  │ Date 2 (YYYY-MM-DD)         │ │              │
│              │  │ [2025-02-15]                │ │              │
│              │  │                             │ │              │
│              │  │ Date 3 (YYYY-MM-DD)         │ │              │
│              │  │ [2025-03-15]                │ │              │
│              │  │                             │ │              │
│              │  │ Date 4 (YYYY-MM-DD)         │ │              │
│              │  │ [2025-04-15]                │ │              │
│              │  │                             │ │              │
│              │  │ [     Upload & Process    ] │ │              │
│              │  └─────────────────────────────┘ │              │
│              │                                 │              │
│              └─────────────────────────────────┘              │
│                                                                 │
│              ┌─────────────────────────────────┐              │
│              │ Upload Progress                 │              │
│              │ ┌─────────────────────────────┐ │              │
│              │ │ ████████████████████ 100%   │ │              │
│              │ │ Processing...               │ │              │
│              │ └─────────────────────────────┘ │              │
│              └─────────────────────────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Mobile Layout (320px - 767px)
```
┌─────────────────────────────────┐
│ [Logo] GeoPulse    [Menu] [User]│
├─────────────────────────────────┤
│                                 │
│ ┌─────────────────────────────┐ │
│ │                             │ │
│ │      Upload New File        │ │
│ │                             │ │
│ │ ┌─────────────────────────┐ │ │
│ │ │                         │ │ │
│ │ │    📁 Drop files here   │ │ │
│ │ │                         │ │ │
│ │ │    [Browse Files]       │ │ │
│ │ │                         │ │ │
│ │ │    .xlsx, .csv (50MB)   │ │ │
│ │ └─────────────────────────┘ │ │
│ │                             │ │
│ │ Engagement Name             │ │
│ │ [_______________________]   │ │
│ │                             │ │
│ │ Date 1                      │ │
│ │ [2025-01-15]                │ │
│ │                             │ │
│ │ Date 2                      │ │
│ │ [2025-02-15]                │ │
│ │                             │ │
│ │ Date 3                      │ │
│ │ [2025-03-15]                │ │
│ │                             │ │
│ │ Date 4                      │ │
│ │ [2025-04-15]                │ │
│ │                             │ │
│ │ [Upload & Process]          │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ Upload Progress             │ │
│ │ ████████████████████ 100%   │ │
│ │ Processing...               │ │
│ └─────────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

### Component Hierarchy
```
FileUploadPage
├── Header
│   ├── Logo
│   ├── UserInfo
│   └── LogoutButton
├── UploadSection
│   ├── Title
│   ├── FileDropZone
│   │   ├── DropArea
│   │   ├── FileInput
│   │   └── FileInfo
│   └── UploadForm
│       ├── EngagementNameInput
│       ├── DateInputs
│       │   ├── Date1Input
│       │   ├── Date2Input
│       │   ├── Date3Input
│       │   └── Date4Input
│       └── UploadButton
└── ProgressSection
    ├── ProgressBar
    ├── StatusMessage
    └── CancelButton
```

---

## Test API Setup

### 1. Mock File Upload API
```javascript
// mock-upload-api.js
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, './uploads/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 50 * 1024 * 1024 // 50MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['.xlsx', '.csv'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowedTypes.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only XLSX and CSV files are allowed.'));
    }
  }
});

// File upload endpoint
app.post('/api/v1/files/upload', upload.single('file'), async (req, res) => {
  try {
    const { engagement_name, date1, date2, date3, date4 } = req.body;
    const file = req.file;

    // Validate required fields
    if (!file) {
      return res.status(400).json({
        status: 'error',
        error_code: 'E001',
        message: 'No file uploaded',
        timestamp: new Date().toISOString()
      });
    }

    if (!engagement_name || !date1 || !date2 || !date3 || !date4) {
      return res.status(422).json({
        status: 'error',
        error_code: 'E007',
        message: 'Missing required fields',
        details: [
          { field: 'engagement_name', message: 'Engagement name is required' },
          { field: 'date1', message: 'Date 1 is required' },
          { field: 'date2', message: 'Date 2 is required' },
          { field: 'date3', message: 'Date 3 is required' },
          { field: 'date4', message: 'Date 4 is required' }
        ],
        timestamp: new Date().toISOString()
      });
    }

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Mock successful response
    const fileId = Math.floor(Math.random() * 1000) + 1;
    const lineCount = Math.floor(Math.random() * 2000) + 500;

    res.json({
      status: 'success',
      data: {
        file_id: fileId,
        filename: file.originalname,
        original_filename: file.originalname,
        engagement_name: engagement_name,
        upload_date: new Date().toISOString().split('T')[0],
        processed_flag: true,
        line_count: lineCount,
        storage_location: `/opt/landrover/123/${new Date().toISOString().split('T')[0]}/output/processed_${file.originalname}`,
        input_location: `/opt/landrover/123/${new Date().toISOString().split('T')[0]}/input/${file.originalname}`,
        processing_time_seconds: 3.2,
        file_size_mb: (file.size / (1024 * 1024)).toFixed(2),
        dates: [date1, date2, date3, date4],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      message: 'File uploaded and processed successfully',
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    res.status(500).json({
      status: 'error',
      error_code: 'E005',
      message: 'File processing failed',
      details: {
        operation: 'file_upload',
        error: error.message
      },
      timestamp: new Date().toISOString()
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(413).json({
        status: 'error',
        error_code: 'E002',
        message: 'File size exceeds maximum limit of 50MB',
        details: {
          field: 'file',
          actual_size_mb: (error.limit / (1024 * 1024)).toFixed(2),
          max_size_mb: 50
        },
        timestamp: new Date().toISOString()
      });
    }
  }

  if (error.message.includes('Invalid file type')) {
    return res.status(400).json({
      status: 'error',
      error_code: 'E001',
      message: 'Invalid file format. Only XLSX and CSV files are allowed.',
      details: {
        field: 'file',
        value: req.file?.originalname,
        allowed_formats: ['xlsx', 'csv']
      },
      timestamp: new Date().toISOString()
    });
  }

  res.status(500).json({
    status: 'error',
    error_code: 'E003',
    message: 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

app.listen(3001, () => {
  console.log('Mock File Upload API running on http://localhost:3001');
});
```

### 2. Test File Generation
```javascript
// test-utils/generate-test-files.js
const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

// Generate test XLSX file
function generateTestXLSX(filename, rows = 100) {
  const data = [];
  
  // Add header row
  data.push(['ID', 'Name', 'Value', 'Date', 'Category']);
  
  // Add data rows
  for (let i = 1; i <= rows; i++) {
    data.push([
      i,
      `Item ${i}`,
      Math.floor(Math.random() * 1000),
      new Date(2025, 0, i).toISOString().split('T')[0],
      ['A', 'B', 'C'][Math.floor(Math.random() * 3)]
    ]);
  }
  
  const ws = XLSX.utils.aoa_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
  
  const filePath = path.join(__dirname, '..', 'test-files', filename);
  XLSX.writeFile(wb, filePath);
  
  return filePath;
}

// Generate test CSV file
function generateTestCSV(filename, rows = 100) {
  let csvContent = 'ID,Name,Value,Date,Category\n';
  
  for (let i = 1; i <= rows; i++) {
    csvContent += `${i},Item ${i},${Math.floor(Math.random() * 1000)},${new Date(2025, 0, i).toISOString().split('T')[0]},${['A', 'B', 'C'][Math.floor(Math.random() * 3)]}\n`;
  }
  
  const filePath = path.join(__dirname, '..', 'test-files', filename);
  fs.writeFileSync(filePath, csvContent);
  
  return filePath;
}

// Generate test files
function generateAllTestFiles() {
  const testFilesDir = path.join(__dirname, '..', 'test-files');
  
  if (!fs.existsSync(testFilesDir)) {
    fs.mkdirSync(testFilesDir, { recursive: true });
  }
  
  // Generate different sized files
  generateTestXLSX('small-test.xlsx', 50);
  generateTestXLSX('medium-test.xlsx', 500);
  generateTestXLSX('large-test.xlsx', 2000);
  
  generateTestCSV('small-test.csv', 50);
  generateTestCSV('medium-test.csv', 500);
  generateTestCSV('large-test.csv', 2000);
  
  console.log('Test files generated successfully!');
}

module.exports = {
  generateTestXLSX,
  generateTestCSV,
  generateAllTestFiles
};
```

---

## Testing Tips

### 1. Unit Testing File Upload Components
```javascript
// FileUploadPage.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import FileUploadPage from '../FileUploadPage';

const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('FileUploadPage', () => {
  beforeEach(() => {
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(() => 'mock-token'),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      },
      writable: true,
    });
  });

  test('renders upload form with all required fields', () => {
    renderWithRouter(<FileUploadPage />);
    
    expect(screen.getByText('Upload New File')).toBeInTheDocument();
    expect(screen.getByLabelText(/engagement name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date 1/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date 2/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date 3/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date 4/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /upload/i })).toBeInTheDocument();
  });

  test('handles file selection via browse button', async () => {
    renderWithRouter(<FileUploadPage />);
    
    const file = new File(['test content'], 'test.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const input = screen.getByLabelText(/browse files/i);
    
    await userEvent.upload(input, file);
    
    expect(screen.getByText('test.xlsx')).toBeInTheDocument();
    expect(screen.getByText(/file selected/i)).toBeInTheDocument();
  });

  test('handles drag and drop file upload', async () => {
    renderWithRouter(<FileUploadPage />);
    
    const file = new File(['test content'], 'test.csv', { type: 'text/csv' });
    const dropZone = screen.getByTestId('file-drop-zone');
    
    fireEvent.dragEnter(dropZone);
    fireEvent.drop(dropZone, {
      dataTransfer: {
        files: [file]
      }
    });
    
    await waitFor(() => {
      expect(screen.getByText('test.csv')).toBeInTheDocument();
    });
  });

  test('validates required fields before upload', async () => {
    renderWithRouter(<FileUploadPage />);
    
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    fireEvent.click(uploadButton);
    
    await waitFor(() => {
      expect(screen.getByText(/engagement name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/date 1 is required/i)).toBeInTheDocument();
      expect(screen.getByText(/date 2 is required/i)).toBeInTheDocument();
      expect(screen.getByText(/date 3 is required/i)).toBeInTheDocument();
      expect(screen.getByText(/date 4 is required/i)).toBeInTheDocument();
    });
  });

  test('validates date format', async () => {
    renderWithRouter(<FileUploadPage />);
    
    const date1Input = screen.getByLabelText(/date 1/i);
    await userEvent.type(date1Input, '2025/01/15');
    
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    fireEvent.click(uploadButton);
    
    await waitFor(() => {
      expect(screen.getByText(/invalid date format/i)).toBeInTheDocument();
    });
  });

  test('handles successful file upload', async () => {
    // Mock successful API response
    const mockResponse = {
      status: 'success',
      data: {
        file_id: 123,
        filename: 'test.xlsx',
        processed_flag: true,
        line_count: 1000
      }
    };
    
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      })
    );
    
    renderWithRouter(<FileUploadPage />);
    
    // Fill form
    await userEvent.type(screen.getByLabelText(/engagement name/i), 'Test Engagement');
    await userEvent.type(screen.getByLabelText(/date 1/i), '2025-01-15');
    await userEvent.type(screen.getByLabelText(/date 2/i), '2025-02-15');
    await userEvent.type(screen.getByLabelText(/date 3/i), '2025-03-15');
    await userEvent.type(screen.getByLabelText(/date 4/i), '2025-04-15');
    
    // Upload file
    const file = new File(['test content'], 'test.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const input = screen.getByLabelText(/browse files/i);
    await userEvent.upload(input, file);
    
    // Submit form
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    fireEvent.click(uploadButton);
    
    await waitFor(() => {
      expect(screen.getByText(/file uploaded successfully/i)).toBeInTheDocument();
    });
  });

  test('shows upload progress', async () => {
    // Mock slow API response
    global.fetch = jest.fn(() =>
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: () => Promise.resolve({ status: 'success' })
        }), 2000)
      )
    );
    
    renderWithRouter(<FileUploadPage />);
    
    // Fill and submit form
    await userEvent.type(screen.getByLabelText(/engagement name/i), 'Test Engagement');
    await userEvent.type(screen.getByLabelText(/date 1/i), '2025-01-15');
    await userEvent.type(screen.getByLabelText(/date 2/i), '2025-02-15');
    await userEvent.type(screen.getByLabelText(/date 3/i), '2025-03-15');
    await userEvent.type(screen.getByLabelText(/date 4/i), '2025-04-15');
    
    const file = new File(['test content'], 'test.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const input = screen.getByLabelText(/browse files/i);
    await userEvent.upload(input, file);
    
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    fireEvent.click(uploadButton);
    
    // Check progress indicator
    expect(screen.getByText(/uploading/i)).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
});
```

### 2. E2E Testing with Cypress
```javascript
// cypress/e2e/file-upload.cy.js
describe('File Upload Page E2E Tests', () => {
  beforeEach(() => {
    // Mock authentication
    cy.window().then((win) => {
      win.localStorage.setItem('token', 'mock-token');
    });
    
    cy.visit('/upload');
  });

  it('should display upload form correctly', () => {
    // Check form elements
    cy.contains('Upload New File').should('be.visible');
    cy.get('[data-testid="engagement-name-input"]').should('be.visible');
    cy.get('[data-testid="date1-input"]').should('be.visible');
    cy.get('[data-testid="date2-input"]').should('be.visible');
    cy.get('[data-testid="date3-input"]').should('be.visible');
    cy.get('[data-testid="date4-input"]').should('be.visible');
    cy.get('[data-testid="upload-button"]').should('be.visible');
  });

  it('should handle file selection via browse button', () => {
    // Upload test file
    cy.fixture('test-file.xlsx').then((fileContent) => {
      cy.get('[data-testid="file-input"]').attachFile({
        fileContent: fileContent,
        fileName: 'test-file.xlsx',
        mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
    });
    
    // Check file is displayed
    cy.contains('test-file.xlsx').should('be.visible');
  });

  it('should handle drag and drop file upload', () => {
    // Mock successful API response
    cy.intercept('POST', '/api/v1/files/upload', {
      statusCode: 200,
      body: {
        status: 'success',
        data: {
          file_id: 123,
          filename: 'test-file.xlsx',
          processed_flag: true
        }
      }
    }).as('uploadRequest');
    
    // Drag and drop file
    cy.get('[data-testid="file-drop-zone"]').attachFile({
      fileContent: 'test content',
      fileName: 'test-file.xlsx',
      mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
    
    // Fill form
    cy.get('[data-testid="engagement-name-input"]').type('Test Engagement');
    cy.get('[data-testid="date1-input"]').type('2025-01-15');
    cy.get('[data-testid="date2-input"]').type('2025-02-15');
    cy.get('[data-testid="date3-input"]').type('2025-03-15');
    cy.get('[data-testid="date4-input"]').type('2025-04-15');
    
    // Submit form
    cy.get('[data-testid="upload-button"]').click();
    
    // Wait for upload
    cy.wait('@uploadRequest');
    
    // Check success message
    cy.contains('File uploaded successfully').should('be.visible');
  });

  it('should show validation errors for missing fields', () => {
    // Try to upload without filling form
    cy.get('[data-testid="upload-button"]').click();
    
    // Check validation messages
    cy.contains('Engagement name is required').should('be.visible');
    cy.contains('Date 1 is required').should('be.visible');
    cy.contains('Date 2 is required').should('be.visible');
    cy.contains('Date 3 is required').should('be.visible');
    cy.contains('Date 4 is required').should('be.visible');
  });

  it('should show error for invalid file type', () => {
    // Upload invalid file type
    cy.get('[data-testid="file-input"]').attachFile({
      fileContent: 'test content',
      fileName: 'test.txt',
      mimeType: 'text/plain'
    });
    
    // Check error message
    cy.contains('Invalid file type').should('be.visible');
    cy.contains('Only XLSX and CSV files are allowed').should('be.visible');
  });

  it('should show error for file too large', () => {
    // Create large file (simulate)
    const largeFile = new Array(60 * 1024 * 1024).join('a'); // 60MB
    
    cy.get('[data-testid="file-input"]').attachFile({
      fileContent: largeFile,
      fileName: 'large-file.xlsx',
      mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
    
    // Check error message
    cy.contains('File size exceeds maximum limit').should('be.visible');
  });

  it('should show upload progress', () => {
    // Mock slow API response
    cy.intercept('POST', '/api/v1/files/upload', {
      delay: 3000,
      statusCode: 200,
      body: { status: 'success' }
    }).as('slowUpload');
    
    // Upload file and submit
    cy.get('[data-testid="file-input"]').attachFile({
      fileContent: 'test content',
      fileName: 'test-file.xlsx',
      mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
    
    cy.get('[data-testid="engagement-name-input"]').type('Test Engagement');
    cy.get('[data-testid="date1-input"]').type('2025-01-15');
    cy.get('[data-testid="date2-input"]').type('2025-02-15');
    cy.get('[data-testid="date3-input"]').type('2025-03-15');
    cy.get('[data-testid="date4-input"]').type('2025-04-15');
    
    cy.get('[data-testid="upload-button"]').click();
    
    // Check progress indicator
    cy.get('[data-testid="progress-bar"]').should('be.visible');
    cy.contains('Uploading').should('be.visible');
    
    // Wait for completion
    cy.wait('@slowUpload');
    cy.contains('Upload complete').should('be.visible');
  });
});
```

---

## UX Styling Guidelines

### 1. File Upload Styling
```css
/* Upload Container */
.upload-container {
  min-height: 100vh;
  background: var(--gray-50);
  padding: 2rem;
}

/* Upload Card */
.upload-card {
  background: var(--white);
  border-radius: 1rem;
  box-shadow: var(--shadow-xl);
  padding: 2.5rem;
  max-width: 600px;
  margin: 0 auto;
  border: 1px solid var(--gray-200);
}

/* File Drop Zone */
.file-drop-zone {
  border: 2px dashed var(--gray-300);
  border-radius: 0.75rem;
  padding: 3rem 2rem;
  text-align: center;
  transition: all 0.2s ease;
  background: var(--gray-50);
  cursor: pointer;
  position: relative;
}

.file-drop-zone:hover {
  border-color: var(--primary-blue);
  background: var(--primary-blue-light);
}

.file-drop-zone.drag-over {
  border-color: var(--primary-blue);
  background: var(--primary-blue-light);
  transform: scale(1.02);
}

.file-drop-zone.has-file {
  border-color: var(--success-green);
  background: var(--success-green);
  color: var(--white);
}

/* File Input */
.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

/* File Info */
.file-info {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--gray-100);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.file-icon {
  font-size: 1.5rem;
  color: var(--primary-blue);
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 600;
  color: var(--gray-800);
}

.file-size {
  font-size: 0.875rem;
  color: var(--gray-600);
}

/* Form Styling */
.upload-form {
  margin-top: 2rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--gray-700);
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--gray-300);
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px var(--primary-blue-light);
}

.form-input.error {
  border-color: var(--error-red);
  box-shadow: 0 0 0 3px rgb(239 68 68 / 0.1);
}

/* Upload Button */
.upload-button {
  width: 100%;
  padding: 1rem 2rem;
  background: var(--primary-blue);
  color: var(--white);
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.upload-button:hover:not(:disabled) {
  background: var(--primary-blue-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

.upload-button:disabled {
  background: var(--gray-400);
  cursor: not-allowed;
  transform: none;
}

/* Progress Section */
.progress-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: var(--gray-100);
  border-radius: 0.75rem;
  display: none;
}

.progress-section.active {
  display: block;
}

.progress-bar {
  width: 100%;
  height: 0.5rem;
  background: var(--gray-200);
  border-radius: 0.25rem;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-fill {
  height: 100%;
  background: var(--primary-blue);
  transition: width 0.3s ease;
  border-radius: 0.25rem;
}

.progress-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--gray-600);
}

/* Responsive Design */
@media (max-width: 768px) {
  .upload-container {
    padding: 1rem;
  }
  
  .upload-card {
    padding: 1.5rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .file-drop-zone {
    padding: 2rem 1rem;
  }
}

@media (max-width: 480px) {
  .upload-card {
    padding: 1rem;
  }
  
  .file-drop-zone {
    padding: 1.5rem 1rem;
  }
}
```

### 2. Best Practices Checklist
- ✅ **Drag & Drop**: Intuitive file upload with visual feedback
- ✅ **File Validation**: Clear error messages for invalid files
- ✅ **Progress Indication**: Real-time upload progress
- ✅ **Form Validation**: Client-side validation with helpful messages
- ✅ **Accessibility**: Keyboard navigation and screen reader support
- ✅ **Mobile Optimization**: Touch-friendly interface
- ✅ **Error Handling**: Graceful error states and recovery
- ✅ **Loading States**: Clear feedback during processing
- ✅ **File Size Limits**: Clear indication of size restrictions
- ✅ **File Type Support**: Visual indication of supported formats
