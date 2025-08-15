import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  Download, 
  Eye, 
  Trash2, 
  Settings, 
  History, 
  LogOut, 
  User,
  FileText,
  CheckCircle,
  Clock,
  BarChart3,
  Search,
  Filter
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useNotification } from '../common/NotificationSystem';
import { dashboardService } from '../../services/api';
import './DashboardPage.css';

const DashboardPage = () => {
  const { user, logout } = useAuth();
  const { showNotification } = useNotification();
  
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      console.log('DashboardPage - Starting to fetch dashboard data');
      console.log('DashboardPage - Current user:', user);
      setLoading(true);
      try {
        console.log('DashboardPage - Calling dashboardService.getDashboardData()');
        const data = await dashboardService.getDashboardData();
        console.log('DashboardPage - Dashboard data received:', data);
        setDashboardData(data);
        console.log('DashboardPage - Dashboard data set successfully');
      } catch (error) {
        console.error('DashboardPage - Error fetching dashboard data:', error);
        showNotification('Failed to load dashboard data', 'error');
        // Set default empty data to prevent crashes
        setDashboardData({
          metrics: {
            total_files: 0,
            processed_files: 0,
            pending_files: 0,
            total_lines: 0
          },
          files: []
        });
      } finally {
        setLoading(false);
        console.log('DashboardPage - Loading finished');
      }
    };

    if (user) {
      console.log('DashboardPage - User exists, fetching dashboard data');
      fetchDashboardData();
    } else {
      console.log('DashboardPage - No user found, not fetching dashboard data');
    }
  }, [user, showNotification]);

  const handleLogout = async () => {
    try {
      await logout();
      showNotification('Logged out successfully', 'success');
    } catch (error) {
      console.error('Logout error:', error);
      showNotification('Error during logout', 'error');
    }
  };

  const handleFileAction = (action, fileId) => {
    console.log(`${action} action for file ${fileId}`);
    // Implement file actions here
  };

  const filteredFiles = (dashboardData?.files || []).filter(file => {
    const matchesStatus = statusFilter === 'all' || 
      (statusFilter === 'processed' && file.processed_flag) ||
      (statusFilter === 'pending' && !file.processed_flag);
    
    const matchesSearch = file.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      file.engagement_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesStatus && matchesSearch;
  });

  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1 className="dashboard-title">Geo Pulse</h1>
          <span className="dashboard-subtitle">Dashboard</span>
        </div>
        <div className="header-right">
          <div className="user-info">
            <div className="user-avatar">
              <User size={20} />
            </div>
            <div className="user-details">
              <span className="user-name">{user?.full_name || user?.email}</span>
              <span className="user-org">{user?.organization || 'Geo Pulse'}</span>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </header>

      {/* Quick Actions */}
      <section className="quick-actions">
        <h2 className="section-title">Quick Actions</h2>
        <div className="actions-grid">
          <button 
            className="action-card"
            onClick={() => window.location.href = '/upload'}
          >
            <Upload size={24} />
            <span>Upload File</span>
          </button>
          <button className="action-card">
            <History size={24} />
            <span>View History</span>
          </button>
          <button className="action-card">
            <Download size={24} />
            <span>Download All</span>
          </button>
          <button className="action-card">
            <Settings size={24} />
            <span>Settings</span>
          </button>
        </div>
      </section>

      {/* Main Content */}
      <main className="dashboard-main">
        {/* Metrics Section */}
        <section className="metrics-section">
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-icon">
                <FileText size={24} />
              </div>
              <div className="metric-content">
                <div className="metric-value">{formatNumber(dashboardData?.metrics?.total_files || 0)}</div>
                <div className="metric-label">Total Files</div>
              </div>
            </div>
            
            <div className="metric-card">
              <div className="metric-icon processed">
                <CheckCircle size={24} />
              </div>
              <div className="metric-content">
                <div className="metric-value">{formatNumber(dashboardData?.metrics?.processed_files || 0)}</div>
                <div className="metric-label">Processed</div>
              </div>
            </div>
            
            <div className="metric-card">
              <div className="metric-icon pending">
                <Clock size={24} />
              </div>
              <div className="metric-content">
                <div className="metric-value">{formatNumber(dashboardData?.metrics?.pending_files || 0)}</div>
                <div className="metric-label">Pending</div>
              </div>
            </div>
            
            <div className="metric-card">
              <div className="metric-icon">
                <BarChart3 size={24} />
              </div>
              <div className="metric-content">
                <div className="metric-value">{formatNumber(dashboardData?.metrics?.total_lines || 0)}</div>
                <div className="metric-label">Total Lines</div>
              </div>
            </div>
          </div>
        </section>

        {/* Files Section */}
        <section className="files-section">
          <div className="files-header">
            <h2 className="section-title">Recent Files</h2>
            <div className="files-actions">
              <div className="search-box">
                <Search size={18} />
                <input
                  type="text"
                  placeholder="Search files..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div className="filter-box">
                <Filter size={18} />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  data-testid="status-filter"
                >
                  <option value="all">All Files</option>
                  <option value="processed">Processed</option>
                  <option value="pending">Pending</option>
                </select>
              </div>
              <button 
                className="upload-btn primary"
                onClick={() => window.location.href = '/upload'}
              >
                <Upload size={18} />
                <span>Upload New File</span>
              </button>
            </div>
          </div>

          <div className="files-table-container">
            <table className="files-table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Engagement</th>
                  <th>Date</th>
                  <th>Lines</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredFiles.map((file) => (
                  <tr key={file.file_id}>
                    <td>
                      <div className="file-info">
                        <FileText size={16} />
                        <span className="filename">{file.filename}</span>
                      </div>
                    </td>
                    <td>
                      <span className="engagement-name">{file.engagement_name}</span>
                    </td>
                    <td>
                      <span className="upload-date">{formatDate(file.upload_date)}</span>
                    </td>
                    <td>
                      <span className="line-count">{formatNumber(file.line_count)}</span>
                    </td>
                    <td>
                      <span className={`status-badge ${file.processed_flag ? 'processed' : 'pending'}`}>
                        {file.processed_flag ? 'Processed' : 'Pending'}
                      </span>
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button
                          className="action-btn view"
                          onClick={() => handleFileAction('view', file.file_id)}
                          title="View File"
                        >
                          <Eye size={16} />
                        </button>
                        {file.processed_flag && (
                          <button
                            className="action-btn download"
                            onClick={() => handleFileAction('download', file.file_id)}
                            title="Download File"
                          >
                            <Download size={16} />
                          </button>
                        )}
                        <button
                          className="action-btn delete"
                          onClick={() => handleFileAction('delete', file.file_id)}
                          title="Delete File"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {filteredFiles.length === 0 && (
              <div className="empty-state">
                <FileText size={48} />
                <h3>No files found</h3>
                <p>Try adjusting your search or filter criteria</p>
              </div>
            )}
          </div>
        </section>


      </main>
    </div>
  );
};

export default DashboardPage;