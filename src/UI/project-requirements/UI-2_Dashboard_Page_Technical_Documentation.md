# UI-2: Dashboard Page - Technical Documentation
## GeoPulse Web Application

**Component:** Dashboard Page  
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
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ Total Files │ │ Processed   │ │ Pending     │ │ Total Lines │ │
│ │     15      │ │    12       │ │     3       │ │   18,500    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Recent Files                    [Upload New File] [+ Button]│ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ Filename          | Date       | Status    | Actions        │ │
│ │ Q1_Financial.xlsx | 2025-08-01 | Processed | [View] [Download]│ │
│ │ Q2_Data.csv       | 2025-07-25 | Pending   | [View] [Delete] │ │
│ │ Q3_Report.xlsx    | 2025-07-20 | Processed | [View] [Download]│ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Quick Actions                                               │ │
│ │ [Upload File] [View History] [Download All] [Settings]     │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Mobile Layout (320px - 767px)
```
┌─────────────────────────────────┐
│ [Logo] GeoPulse    [Menu] [User]│
├─────────────────────────────────┤
│                                 │
│ ┌─────────────┐ ┌─────────────┐ │
│ │ Total Files │ │ Processed   │ │
│ │     15      │ │    12       │ │
│ └─────────────┘ └─────────────┘ │
│ ┌─────────────┐ ┌─────────────┐ │
│ │ Pending     │ │ Total Lines │ │
│ │     3       │ │   18,500    │ │
│ └─────────────┘ └─────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ Recent Files [+ Upload]     │ │
│ ├─────────────────────────────┤ │
│ │ Q1_Financial.xlsx           │ │
│ │ 2025-08-01 | Processed      │ │
│ │ [View] [Download]           │ │
│ ├─────────────────────────────┤ │
│ │ Q2_Data.csv                 │ │
│ │ 2025-07-25 | Pending        │ │
│ │ [View] [Delete]             │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ Quick Actions               │ │
│ │ [Upload] [History] [Settings]│ │
│ └─────────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

### Component Hierarchy
```
DashboardPage
├── Header
│   ├── Logo
│   ├── UserInfo
│   └── LogoutButton
├── MetricsSection
│   ├── TotalFilesCard
│   ├── ProcessedFilesCard
│   ├── PendingFilesCard
│   └── TotalLinesCard
├── FilesSection
│   ├── SectionHeader
│   ├── UploadButton
│   ├── FilesTable
│   └── Pagination
└── QuickActions
    ├── UploadFileButton
    ├── ViewHistoryButton
    └── SettingsButton
```

---

## Test API Setup

### 1. Mock Dashboard API
```javascript
// mock-dashboard-api.js
const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Mock dashboard data
const dashboardData = {
  user: {
    user_id: 123,
    user_name: "John Doe",
    email: "john.doe@acmecorp.com",
    organization_name: "Acme Corporation",
    logo_path: "/uploads/logos/acme_logo.png"
  },
  files: [
    {
      file_id: 456,
      filename: "Q1_Financial_Data.xlsx",
      original_filename: "Q1_Financial_Data.xlsx",
      upload_date: "2025-08-01",
      engagement_name: "Q1 Financial Analysis",
      processed_flag: true,
      line_count: 1250,
      storage_location: "/opt/landrover/123/2025-08-01/output/processed_Q1_Financial_Data.xlsx"
    },
    {
      file_id: 457,
      filename: "Q2_Data.csv",
      original_filename: "Q2_Data.csv",
      upload_date: "2025-07-25",
      engagement_name: "Q2 Quarterly Review",
      processed_flag: false,
      line_count: 890,
      storage_location: "/opt/landrover/123/2025-07-25/input/Q2_Data.csv"
    }
  ],
  metrics: {
    total_files: 15,
    processed_files: 12,
    pending_files: 3,
    total_lines: 18500,
    average_lines_per_file: 1233,
    files_this_month: 5,
    files_this_week: 2,
    storage_used_mb: 45.2
  },
  pagination: {
    current_page: 1,
    total_pages: 3,
    total_items: 15,
    items_per_page: 20,
    has_next: true,
    has_previous: false
  }
};

// Dashboard endpoint
app.get('/api/v1/dashboard', (req, res) => {
  const { limit = 20, offset = 0, sort_by = 'upload_date', sort_order = 'desc', status = 'all' } = req.query;
  
  // Simulate filtering
  let filteredFiles = dashboardData.files;
  if (status !== 'all') {
    filteredFiles = dashboardData.files.filter(file => 
      status === 'processed' ? file.processed_flag : !file.processed_flag
    );
  }
  
  // Simulate pagination
  const paginatedFiles = filteredFiles.slice(offset, offset + parseInt(limit));
  
  res.json({
    status: 'success',
    data: {
      ...dashboardData,
      files: paginatedFiles
    },
    message: 'Dashboard data retrieved successfully',
    timestamp: new Date().toISOString()
  });
});

app.listen(3001, () => {
  console.log('Mock Dashboard API running on http://localhost:3001');
});
```

### 2. Test Data Configuration
```javascript
// test-data/dashboard-test-data.js
export const mockDashboardData = {
  user: {
    user_id: 123,
    user_name: "John Doe",
    email: "john.doe@acmecorp.com",
    organization_name: "Acme Corporation"
  },
  files: [
    {
      file_id: 1,
      filename: "Q1_Financial_Data.xlsx",
      upload_date: "2025-08-01",
      processed_flag: true,
      line_count: 1250
    },
    {
      file_id: 2,
      filename: "Q2_Data.csv",
      upload_date: "2025-07-25",
      processed_flag: false,
      line_count: 890
    }
  ],
  metrics: {
    total_files: 15,
    processed_files: 12,
    pending_files: 3,
    total_lines: 18500
  }
};

export const testScenarios = [
  {
    name: 'Empty Dashboard',
    files: [],
    metrics: { total_files: 0, processed_files: 0, pending_files: 0, total_lines: 0 }
  },
  {
    name: 'Many Files',
    files: Array.from({ length: 50 }, (_, i) => ({
      file_id: i + 1,
      filename: `File_${i + 1}.xlsx`,
      upload_date: '2025-08-01',
      processed_flag: i % 2 === 0,
      line_count: 1000 + i
    })),
    metrics: { total_files: 50, processed_files: 25, pending_files: 25, total_lines: 50000 }
  }
];
```

---

## Testing Tips

### 1. Unit Testing Dashboard Components
```javascript
// DashboardPage.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import DashboardPage from '../DashboardPage';

const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('DashboardPage', () => {
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

  test('renders dashboard with user information', async () => {
    renderWithRouter(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Acme Corporation')).toBeInTheDocument();
    });
  });

  test('displays metrics cards correctly', async () => {
    renderWithRouter(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText('15')).toBeInTheDocument(); // Total files
      expect(screen.getByText('12')).toBeInTheDocument(); // Processed files
      expect(screen.getByText('3')).toBeInTheDocument();  // Pending files
      expect(screen.getByText('18,500')).toBeInTheDocument(); // Total lines
    });
  });

  test('displays files table with correct data', async () => {
    renderWithRouter(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Q1_Financial_Data.xlsx')).toBeInTheDocument();
      expect(screen.getByText('Q2_Data.csv')).toBeInTheDocument();
      expect(screen.getByText('Processed')).toBeInTheDocument();
      expect(screen.getByText('Pending')).toBeInTheDocument();
    });
  });

  test('handles file actions correctly', async () => {
    renderWithRouter(<DashboardPage />);
    
    await waitFor(() => {
      const viewButtons = screen.getAllByText('View');
      const downloadButtons = screen.getAllByText('Download');
      
      expect(viewButtons).toHaveLength(2);
      expect(downloadButtons).toHaveLength(1); // Only processed files
    });
  });

  test('filters files by status', async () => {
    renderWithRouter(<DashboardPage />);
    
    await waitFor(() => {
      const statusFilter = screen.getByLabelText(/status/i);
      fireEvent.change(statusFilter, { target: { value: 'processed' } });
      
      // Should only show processed files
      expect(screen.getByText('Q1_Financial_Data.xlsx')).toBeInTheDocument();
      expect(screen.queryByText('Q2_Data.csv')).not.toBeInTheDocument();
    });
  });
});
```

### 2. E2E Testing with Cypress
```javascript
// cypress/e2e/dashboard.cy.js
describe('Dashboard Page E2E Tests', () => {
  beforeEach(() => {
    // Mock authentication
    cy.window().then((win) => {
      win.localStorage.setItem('token', 'mock-token');
    });
    
    // Mock API response
    cy.intercept('GET', '/api/v1/dashboard*', {
      statusCode: 200,
      body: {
        status: 'success',
        data: {
          user: {
            user_id: 123,
            user_name: 'John Doe',
            organization_name: 'Acme Corporation'
          },
          files: [
            {
              file_id: 1,
              filename: 'Q1_Financial_Data.xlsx',
              processed_flag: true,
              line_count: 1250
            }
          ],
          metrics: {
            total_files: 15,
            processed_files: 12,
            pending_files: 3,
            total_lines: 18500
          }
        }
      }
    }).as('dashboardRequest');
    
    cy.visit('/dashboard');
    cy.wait('@dashboardRequest');
  });

  it('should display dashboard elements correctly', () => {
    // Check metrics cards
    cy.contains('15').should('be.visible'); // Total files
    cy.contains('12').should('be.visible'); // Processed files
    cy.contains('3').should('be.visible');  // Pending files
    cy.contains('18,500').should('be.visible'); // Total lines
    
    // Check user info
    cy.contains('John Doe').should('be.visible');
    cy.contains('Acme Corporation').should('be.visible');
    
    // Check files table
    cy.contains('Q1_Financial_Data.xlsx').should('be.visible');
    cy.contains('Processed').should('be.visible');
  });

  it('should handle file actions', () => {
    // Click view button
    cy.contains('View').first().click();
    cy.url().should('include', '/files/1');
    
    // Go back to dashboard
    cy.go('back');
    
    // Click download button
    cy.contains('Download').first().click();
    // Should trigger file download
  });

  it('should filter files by status', () => {
    // Select processed filter
    cy.get('[data-testid="status-filter"]').select('processed');
    
    // Should only show processed files
    cy.contains('Processed').should('be.visible');
    cy.contains('Pending').should('not.exist');
  });

  it('should handle pagination', () => {
    // Mock many files
    cy.intercept('GET', '/api/v1/dashboard*', {
      statusCode: 200,
      body: {
        status: 'success',
        data: {
          files: Array.from({ length: 25 }, (_, i) => ({
            file_id: i + 1,
            filename: `File_${i + 1}.xlsx`,
            processed_flag: true,
            line_count: 1000
          })),
          pagination: {
            current_page: 1,
            total_pages: 2,
            has_next: true
          }
        }
      }
    }).as('paginationRequest');
    
    cy.visit('/dashboard');
    cy.wait('@paginationRequest');
    
    // Click next page
    cy.contains('Next').click();
    cy.url().should('include', 'page=2');
  });
});
```

---

## UX Styling Guidelines

### 1. Dashboard Layout CSS
```css
/* Dashboard Container */
.dashboard-container {
  min-height: 100vh;
  background: var(--gray-50);
}

/* Header */
.dashboard-header {
  background: var(--white);
  border-bottom: 1px solid var(--gray-200);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-sm);
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}

.metric-card {
  background: var(--white);
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--gray-200);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-blue);
  margin-bottom: 0.5rem;
}

.metric-label {
  font-size: 0.875rem;
  color: var(--gray-600);
  font-weight: 500;
}

/* Files Section */
.files-section {
  background: var(--white);
  margin: 0 2rem 2rem;
  border-radius: 0.75rem;
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.files-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--gray-200);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.files-table {
  width: 100%;
  border-collapse: collapse;
}

.files-table th,
.files-table td {
  padding: 1rem 1.5rem;
  text-align: left;
  border-bottom: 1px solid var(--gray-200);
}

.files-table th {
  background: var(--gray-50);
  font-weight: 600;
  color: var(--gray-700);
  font-size: 0.875rem;
}

/* Status Badges */
.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-processed {
  background: var(--success-green);
  color: var(--white);
}

.status-pending {
  background: var(--warning-orange);
  color: var(--white);
}

/* Action Buttons */
.action-button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-right: 0.5rem;
}

.btn-view {
  background: var(--primary-blue);
  color: var(--white);
}

.btn-download {
  background: var(--success-green);
  color: var(--white);
}

.btn-delete {
  background: var(--error-red);
  color: var(--white);
}

/* Responsive Design */
@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    padding: 1rem;
  }
  
  .files-section {
    margin: 0 1rem 1rem;
  }
  
  .files-table {
    font-size: 0.875rem;
  }
  
  .files-table th,
  .files-table td {
    padding: 0.75rem;
  }
}

@media (max-width: 480px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }
}
```

### 2. Best Practices Checklist
- ✅ **Responsive Grid**: Use CSS Grid for flexible layouts
- ✅ **Card Design**: Consistent card styling with hover effects
- ✅ **Status Indicators**: Clear visual status badges
- ✅ **Loading States**: Skeleton screens during data loading
- ✅ **Error Handling**: User-friendly error messages
- ✅ **Accessibility**: Proper ARIA labels and keyboard navigation
- ✅ **Performance**: Lazy loading for large datasets
- ✅ **Mobile First**: Optimize for mobile devices first
- ✅ **Consistent Spacing**: Use design system spacing
- ✅ **Color Hierarchy**: Clear visual hierarchy with colors
