import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import {
  BarChart3,
  FileText,
  Upload,
  Download,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  RefreshCw,
  Search
} from 'lucide-react';
import { format } from 'date-fns';

// Helper function to format dates in IST
const formatDateIST = (dateString) => {
  try {
    if (!dateString) return 'N/A';
    
    // Handle different date formats
    let date;
    if (typeof dateString === 'string') {
      // If it's already in ISO format, use it directly
      if (dateString.includes('T')) {
        date = new Date(dateString);
      } else {
        // Add time component for proper parsing
        date = new Date(dateString + 'T00:00:00.000Z');
      }
    } else {
      date = new Date(dateString);
    }
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      return 'Invalid Date';
    }
    
    // Convert to IST timezone (UTC+5:30)
    const istDate = new Date(date.getTime() + (5.5 * 60 * 60 * 1000));
    return format(istDate, 'dd/MM/yyyy');
  } catch (error) {
    console.error('Error formatting date:', error, 'Date string:', dateString);
    return 'Invalid Date';
  }
};

// Helper function to get download filename
const getDownloadFilename = (filename) => {
  if (!filename) return 'processed_file.xlsx';
  
  // If it's already an XLSX file, return as is
  if (filename.toLowerCase().endsWith('.xlsx')) {
    return filename;
  }
  
  // If it's a CSV file, convert to XLSX
  if (filename.toLowerCase().endsWith('.csv')) {
    return filename.replace(/\.csv$/i, '.xlsx');
  }
  
  // If it doesn't have an extension, add .xlsx
  if (!filename.includes('.')) {
    return `${filename}.xlsx`;
  }
  
  // For any other extension, replace with .xlsx
  return filename.replace(/\.[^.]*$/i, '.xlsx');
};

const Dashboard = () => {
  const { user, token } = useAuth();
  const location = useLocation();
  
  // Demo data for when backend is not available
  const demoData = {
    files: [
      {
        file_id: 1,
        filename: 'sample_data_2024_processed.xlsx',
        original_filename: 'sample_data_2024.csv',
        engagement_name: 'GeoPulse Analysis Project',
        upload_date: new Date().toISOString().split('T')[0], // Today's date
        processed_flag: true,
        line_count: 15420,
        file_size_mb: 2.45
      },
      {
        file_id: 2,
        filename: 'geo_analysis_beta_processed.xlsx',
        original_filename: 'geo_analysis_beta.csv',
        engagement_name: 'Satellite Data Processing',
        upload_date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Yesterday
        processed_flag: false,
        line_count: 8750,
        file_size_mb: 1.78
      },
      {
        file_id: 3,
        filename: 'location_data_gamma_processed.xlsx',
        original_filename: 'location_data_gamma.csv',
        engagement_name: 'Forest Land Analysis',
        upload_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 2 days ago
        processed_flag: true,
        line_count: 22100,
        file_size_mb: 3.12
      }
    ]
  };

  const [dashboardData, setDashboardData] = useState(demoData);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('upload_date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [dateFilter, setDateFilter] = useState('all'); // New filter for date segregation
  const [apiConnected, setApiConnected] = useState(false);
  const [downloadingFiles, setDownloadingFiles] = useState(new Set()); // Track downloading files

  // Load initial data and handle auto-refresh
  useEffect(() => {
    // Load initial data when component mounts
    handleRefresh();
  }, []);

  // Auto-refresh dashboard when coming from upload page
  useEffect(() => {
    if (location.state?.refreshDashboard) {
      handleRefresh();
      // Clear the refresh flag
      window.history.replaceState({}, document.title);
    }
  }, [location.state?.refreshDashboard]);

  const handleDownload = async (fileId, filename) => {
    try {
      // Check if user is logged in
      if (!user || !token) {
        toast.error('Please log in to download files');
        return;
      }

      // Check if this is demo mode (fake token)
      if (token.startsWith('demo-token-')) {
        toast.error('Download is not available in demo mode. Please log in with a real account.');
        return;
      }

      // Check if file is processed
      const file = dashboardData?.files?.find(f => f.file_id === fileId);
      if (!file) {
        toast.error('File not found in dashboard data');
        return;
      }

      if (!file.processed_flag) {
        toast.error('File is not yet processed. Please wait for processing to complete.');
        return;
      }

      // Set downloading state
      setDownloadingFiles(prev => new Set([...prev, fileId]));

      console.log(`Attempting to download file ${fileId}: ${filename}`);

      const response = await axios.get(`/api/v1/files/${fileId}/download`, {
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        timeout: 30000 // 30 second timeout for file downloads
      });

      // Check if response has content
      if (!response.data || response.data.size === 0) {
        throw new Error('Downloaded file is empty');
      }

      // Get the correct download filename
      const downloadFilename = getDownloadFilename(filename);

      // Create blob URL and trigger download
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', downloadFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      console.log(`Successfully downloaded file: ${downloadFilename}`);
      toast.success(`File downloaded successfully: ${downloadFilename}`);
    } catch (error) {
      console.error('Download error:', error);
      if (error.response?.status === 401) {
        toast.error('Authentication failed. Please log in again. Please log out and log in with your real account.');
        // Clear invalid token
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.reload();
      } else if (error.response?.status === 404) {
        toast.error('File not found on server.');
      } else if (error.response?.status === 403) {
        toast.error('Access denied. You do not have permission to download this file.');
      } else if (error.code === 'ECONNABORTED') {
        toast.error('Download timeout. Please try again.');
      } else if (error.message === 'Downloaded file is empty') {
        toast.error('Downloaded file is empty. Please contact support.');
      } else {
        toast.error(`Download failed: ${error.response?.data?.detail || error.message}`);
      }
    } finally {
      // Clear downloading state
      setDownloadingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });
    }
  };

  const handleView = async (file) => {
    try {
      // Check if user is logged in
      if (!user || !token) {
        toast.error('Please log in to view results');
        return;
      }

      // Check if this is demo mode (fake token)
      if (token.startsWith('demo-token-')) {
        toast.error('View is not available in demo mode. Please log in with a real account.');
        return;
      }

      // Check if file is processed
      if (!file.processed_flag) {
        toast.error('File is not yet processed. Please wait for processing to complete.');
        return;
      }

      console.log(`Attempting to view HTML results for file ${file.file_id}: ${file.filename}`);

      // First, fetch the HTML content with authentication
      const response = await axios.get(`/api/v1/files/${file.file_id}/view`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        timeout: 30000
      });

      // Create a blob URL with the HTML content
      const blob = new Blob([response.data], { type: 'text/html' });
      const htmlUrl = window.URL.createObjectURL(blob);
      
      // Open the HTML content in a new tab
      const newWindow = window.open(htmlUrl, '_blank');
      
      if (!newWindow) {
        toast.error('Please allow pop-ups to view results in a new tab');
        window.URL.revokeObjectURL(htmlUrl);
        return;
      }

      // Clean up the blob URL after a delay
      setTimeout(() => {
        window.URL.revokeObjectURL(htmlUrl);
      }, 1000);

      toast.success('Opening results in new tab...');
      
    } catch (error) {
      console.error('View error:', error);
      if (error.response?.status === 401) {
        toast.error('Authentication failed. Please log in again.');
        // Clear invalid token
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.reload();
      } else if (error.response?.status === 404) {
        toast.error('Results not found on server.');
      } else if (error.response?.status === 403) {
        toast.error('Access denied. You do not have permission to view this file.');
      } else {
        toast.error(`Failed to view results: ${error.response?.data?.detail || error.message}`);
      }
    }
  };

  const handleHide = (fileId) => {
    setHiddenFiles(prev => new Set([...prev, fileId]));
    toast.success('File hidden from view');
  };

  const handleUnhide = (fileId) => {
    setHiddenFiles(prev => {
      const newSet = new Set(prev);
      newSet.delete(fileId);
      return newSet;
    });
    toast.success('File unhidden');
  };

  const handleRefresh = async () => {
    setLoading(true);

    // Check if user is logged in
    if (!user) {
      console.log('User not logged in, cannot connect to API');
      setApiConnected(false);
      setLoading(false);
      return;
    }

    try {
      const response = await axios.get('/api/v1/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: {
          limit: 50,
          offset: 0,
          sort_by: sortBy,
          sort_order: sortOrder,
          status: statusFilter,
        },
        timeout: 10000 // 10 second timeout
      });

      console.log('Dashboard API response:', response.data);
      
      if (response.data.status === 'success') {
        setDashboardData(response.data.data);
        setApiConnected(true);
        console.log('Dashboard data updated from API');
      } else {
        console.log('API returned non-success status:', response.data.status);
        setApiConnected(false);
      }
    } catch (error) {
      console.error('API connection failed:', error);
      console.error('Error details:', error.response?.data);
      setApiConnected(false);
      // Show error for debugging in production
      if (error.response?.status === 401) {
        toast.error('Authentication failed. Please log in again.');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.reload();
      } else if (error.response?.status === 500) {
        toast.error('Server error. Please try again later.');
      } else if (error.code === 'ECONNABORTED') {
        toast.error('Request timeout. Please check your connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Helper function to check if date is today
  const isToday = (dateString) => {
    const today = new Date();
    const fileDate = new Date(dateString);
    return today.toDateString() === fileDate.toDateString();
  };

  // Helper function to check if date is yesterday
  const isYesterday = (dateString) => {
    const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const fileDate = new Date(dateString);
    return yesterday.toDateString() === fileDate.toDateString();
  };

  const filteredFiles = dashboardData?.files?.filter(file => {
    const matchesSearch = file.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      file.engagement_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' ||
      (statusFilter === 'processed' && file.processed_flag) ||
      (statusFilter === 'pending' && !file.processed_flag);
    
    // Date filter logic
    let matchesDate = true;
    if (dateFilter === 'today') {
      matchesDate = isToday(file.upload_date);
    } else if (dateFilter === 'yesterday') {
      matchesDate = isYesterday(file.upload_date);
    } else if (dateFilter === 'this_week') {
      const fileDate = new Date(file.upload_date);
      const today = new Date();
      const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
      matchesDate = fileDate >= weekAgo;
    }
    
    return matchesSearch && matchesStatus && matchesDate;
  }) || [];

  // Add state for hidden files
  const [hiddenFiles, setHiddenFiles] = useState(new Set());
  const [showHidden, setShowHidden] = useState(false);
  
  // Filter state
  const [filters, setFilters] = useState({
    state: 'Andhra Pradesh',
    district: 'Nellore',
    division: 'Rapur'
  });

  // Sort filtered files
  const sortedFiles = [...filteredFiles].sort((a, b) => {
    let aValue, bValue;
    
    switch (sortBy) {
      case 'filename':
        aValue = a.filename.toLowerCase();
        bValue = b.filename.toLowerCase();
        break;
      case 'engagement_name':
        aValue = a.engagement_name.toLowerCase();
        bValue = b.engagement_name.toLowerCase();
        break;
      case 'file_size_mb':
        aValue = a.file_size_mb || 0;
        bValue = b.file_size_mb || 0;
        break;
      case 'line_count':
        aValue = a.line_count || 0;
        bValue = b.line_count || 0;
        break;
      case 'upload_date':
      default:
        aValue = new Date(a.upload_date);
        bValue = new Date(b.upload_date);
        break;
    }
    
    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  // Filter files based on hidden state
  const visibleFiles = showHidden 
    ? sortedFiles 
    : sortedFiles.filter(file => !hiddenFiles.has(file.file_id));

  const metrics = {
    totalFiles: dashboardData?.files?.length || 0,
    processedFiles: dashboardData?.files?.filter(f => f.processed_flag).length || 0,
    pendingFiles: dashboardData?.files?.filter(f => !f.processed_flag).length || 0,
    totalLines: dashboardData?.files?.reduce((sum, f) => sum + (f.line_count || 0), 0) || 0,
    todayFiles: dashboardData?.files?.filter(f => isToday(f.upload_date)).length || 0,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        <span className="ml-2 text-gray-600">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">

             {/* Header */}
       <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
         <div>
           <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
           <p className="mt-1 text-sm text-gray-500">
             Welcome back, {user?.user_name}
             {token?.startsWith('demo-token-') && (
               <span className="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                 Demo Mode
               </span>
             )}
           </p>
         </div>
                 <div className="mt-4 sm:mt-0 flex space-x-3">
           <button
             onClick={handleRefresh}
             className="btn-secondary flex items-center"
           >
             <RefreshCw className="h-4 w-4 mr-2" />
             Refresh
           </button>
           {hiddenFiles.size > 0 && (
             <button
               onClick={() => setShowHidden(!showHidden)}
               className={`btn-secondary flex items-center ${showHidden ? 'bg-yellow-100 text-yellow-800' : ''}`}
             >
               <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
               </svg>
               {showHidden ? 'Hide Files' : `Show Hidden (${hiddenFiles.size})`}
             </button>
           )}
           <Link to="/upload" className="btn-primary flex items-center">
             <Upload className="h-4 w-4 mr-2" />
             Upload File
           </Link>
         </div>
      </div>

             {/* Demo Mode Notice */}
       {token?.startsWith('demo-token-') && (
         <div className="card bg-yellow-50 border-yellow-200">
           <div className="flex items-center">
             <div className="flex-shrink-0">
               <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                 <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
               </svg>
             </div>
             <div className="ml-3">
               <h3 className="text-sm font-medium text-yellow-800">
                 Demo Mode Active
               </h3>
               <div className="mt-2 text-sm text-yellow-700">
                 <p>
                   You are currently in demo mode. Some features like file downloads are not available. 
                   <button 
                     onClick={() => {
                       localStorage.removeItem('token');
                       localStorage.removeItem('user');
                       window.location.href = '/login';
                     }}
                     className="ml-2 underline hover:no-underline font-medium"
                   >
                     Log in with a real account
                   </button>
                   to access all features.
                 </p>
               </div>
             </div>
           </div>
         </div>
       )}

       {/* Filter Section */}
       <div className="card">
         <h2 className="text-lg font-medium text-gray-900 mb-4">Filter Data</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* State Filter */}
          <div>
            <label htmlFor="state" className="block text-sm font-medium text-gray-700 mb-1">
              State
            </label>
            <select
              id="state"
              value={filters.state}
              onChange={(e) => setFilters(prev => ({ ...prev, state: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="Andhra Pradesh">Andhra Pradesh</option>
            </select>
          </div>

          {/* District Filter */}
          <div>
            <label htmlFor="district" className="block text-sm font-medium text-gray-700 mb-1">
              District
            </label>
            <select
              id="district"
              value={filters.district}
              onChange={(e) => setFilters(prev => ({ ...prev, district: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="Nellore">Nellore</option>
              <option value="Visakhapatnam">Visakhapatnam</option>
              <option value="Vijayawada">Vijayawada</option>
              <option value="Guntur">Guntur</option>
              <option value="Kurnool">Kurnool</option>
              <option value="Kakinada">Kakinada</option>
              <option value="Kadapa">Kadapa</option>
              <option value="Tirupati">Tirupati</option>
              <option value="Anantapuramu">Anantapuramu</option>
              <option value="Vizianagaram">Vizianagaram</option>
              <option value="Eluru">Eluru</option>
              <option value="Nandyal">Nandyal</option>
              <option value="Ongole">Ongole</option>
              <option value="Adoni">Adoni</option>
              <option value="Madanapalle">Madanapalle</option>
              <option value="Machilipatnam">Machilipatnam</option>
              <option value="Tenali">Tenali</option>
              <option value="Proddatur">Proddatur</option>
              <option value="Chittoor">Chittoor</option>
              <option value="Hindupur">Hindupur</option>
              <option value="Srikakulam">Srikakulam</option>
              <option value="Bhimavaram">Bhimavaram</option>
              <option value="Tadepalligudem">Tadepalligudem</option>
            </select>
          </div>

          {/* Division Filter */}
          <div>
            <label htmlFor="division" className="block text-sm font-medium text-gray-700 mb-1">
              Division
            </label>
            <select
              id="division"
              value={filters.division}
              onChange={(e) => setFilters(prev => ({ ...prev, division: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="Rapur">Rapur</option>
              <option value="Alluri Sitharama Raju">Alluri Sitharama Raju</option>
              <option value="Anakapalli">Anakapalli</option>
              <option value="Anantapuramu">Anantapuramu</option>
              <option value="Annamayya">Annamayya</option>
              <option value="Bapatla">Bapatla</option>
              <option value="Chittoor">Chittoor</option>
              <option value="East Godavari">East Godavari</option>
              <option value="Eluru">Eluru</option>
              <option value="Guntur">Guntur</option>
              <option value="Kakinada">Kakinada</option>
              <option value="Krishna">Krishna</option>
              <option value="Kurnool">Kurnool</option>
              <option value="Nandyal">Nandyal</option>
              <option value="Nellore">Nellore</option>
              <option value="NTR">NTR</option>
              <option value="Palnadu">Palnadu</option>
              <option value="Prakasam">Prakasam</option>
              <option value="Srikakulam">Srikakulam</option>
              <option value="Sri Sathya Sai">Sri Sathya Sai</option>
              <option value="Tirupati">Tirupati</option>
            </select>
          </div>
        </div>
      </div>

             {/* Metrics Cards */}
       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
         <div className="card">
           <div className="flex items-center">
             <div className="flex-shrink-0">
               <FileText className="h-8 w-8 text-primary-600" />
             </div>
             <div className="ml-4">
               <p className="text-sm font-medium text-gray-500">Total Files</p>
               <p className="text-2xl font-semibold text-gray-900">{metrics.totalFiles}</p>
             </div>
           </div>
         </div>

         <div className="card">
           <div className="flex items-center">
             <div className="flex-shrink-0">
               <CheckCircle className="h-8 w-8 text-green-600" />
             </div>
             <div className="ml-4">
               <p className="text-sm font-medium text-gray-500">Processed</p>
               <p className="text-2xl font-semibold text-gray-900">{metrics.processedFiles}</p>
             </div>
           </div>
         </div>

         <div className="card">
           <div className="flex items-center">
             <div className="flex-shrink-0">
               <Clock className="h-8 w-8 text-yellow-600" />
             </div>
             <div className="ml-4">
               <p className="text-sm font-medium text-gray-500">Pending</p>
               <p className="text-2xl font-semibold text-gray-900">{metrics.pendingFiles}</p>
             </div>
           </div>
         </div>

         <div className="card">
           <div className="flex items-center">
             <div className="flex-shrink-0">
               <BarChart3 className="h-8 w-8 text-blue-600" />
             </div>
             <div className="ml-4">
               <p className="text-sm font-medium text-gray-500">Today's Files</p>
               <p className="text-2xl font-semibold text-gray-900">{metrics.todayFiles}</p>
             </div>
           </div>
         </div>

         <div className="card">
           <div className="flex items-center">
             <div className="flex-shrink-0">
               <BarChart3 className="h-8 w-8 text-purple-600" />
             </div>
             <div className="ml-4">
               <p className="text-sm font-medium text-gray-500">Total Records</p>
               <p className="text-2xl font-semibold text-gray-900">{metrics.totalLines.toLocaleString()}</p>
             </div>
           </div>
         </div>
       </div>

      {/* Files Section */}
      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
          <div className="flex items-center space-x-3">
            <h2 className="text-lg font-medium text-gray-900">Recent Files</h2>
            {!apiConnected && (
              <div className="flex items-center space-x-2 px-3 py-1 bg-yellow-100 border border-yellow-300 rounded-full">
                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-yellow-700 font-medium">Demo Mode</span>
              </div>
            )}
            {apiConnected && (
              <div className="flex items-center space-x-2 px-3 py-1 bg-green-100 border border-green-300 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-xs text-green-700 font-medium">Live Data</span>
              </div>
            )}
          </div>

                     {/* Filters */}
           <div className="mt-4 sm:mt-0 flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
             <div className="relative">
               <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
               <input
                 type="text"
                 placeholder="Search by project name or file name..."
                 value={searchTerm}
                 onChange={(e) => setSearchTerm(e.target.value)}
                 className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
               />
             </div>

             <select
               value={statusFilter}
               onChange={(e) => setStatusFilter(e.target.value)}
               className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
             >
               <option value="all">All Status</option>
               <option value="processed">Processed</option>
               <option value="pending">Pending</option>
             </select>

             <select
               value={dateFilter}
               onChange={(e) => setDateFilter(e.target.value)}
               className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
             >
               <option value="all">All Dates</option>
               <option value="today">Today</option>
               <option value="yesterday">Yesterday</option>
               <option value="this_week">This Week</option>
             </select>

             <select
               value={sortBy}
               onChange={(e) => setSortBy(e.target.value)}
               className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
             >
               <option value="upload_date">Upload Date (Latest First)</option>
               <option value="filename">File Name (A-Z)</option>
               <option value="engagement_name">Project Name (A-Z)</option>
               <option value="file_size_mb">File Size (Largest First)</option>
               <option value="line_count">Records Count (Highest First)</option>
             </select>

             <button
               onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
               className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
               title={sortOrder === 'asc' ? 'Sort Ascending' : 'Sort Descending'}
             >
               {sortOrder === 'asc' ? '↑' : '↓'}
             </button>
           </div>
        </div>

        {/* Files Table */}
        <div className="overflow-x-auto">
                     <table className="min-w-full divide-y divide-gray-200">
             <thead className="bg-gray-50">
               <tr>
                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                   Project Name
                 </th>
                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                   File Name
                 </th>
                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                   Upload Date
                 </th>
                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                   Status
                 </th>
                                   <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    File Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
               </tr>
             </thead>
                         <tbody className="bg-white divide-y divide-gray-200">
               {visibleFiles.length === 0 ? (
                 <tr>
                   <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                     No files found
                   </td>
                 </tr>
               ) : (
                 visibleFiles.map((file) => (
                   <tr key={file.file_id} className="hover:bg-gray-50">
                     {/* Project Name */}
                     <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                       {file.engagement_name}
                     </td>
                     
                     {/* File Name */}
                     <td className="px-6 py-4 whitespace-nowrap">
                       <div className="flex items-center">
                         <FileText className="h-5 w-5 text-gray-400 mr-2" />
                         <div>
                           <div className="text-sm font-medium text-gray-900">
                             {file.filename}
                           </div>
                           <div className="text-sm text-gray-500">
                             {file.original_filename}
                           </div>
                         </div>
                       </div>
                     </td>
                     
                                           {/* Upload Date */}
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {isToday(file.upload_date) ? (
                          <span className="text-green-600 font-medium">Today</span>
                        ) : isYesterday(file.upload_date) ? (
                          <span className="text-blue-600 font-medium">Yesterday</span>
                        ) : (
                          formatDateIST(file.upload_date)
                        )}
                      </td>
                     
                     {/* Status */}
                     <td className="px-6 py-4 whitespace-nowrap">
                       {file.processed_flag ? (
                         <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                           <CheckCircle className="h-3 w-3 mr-1" />
                           Processed
                         </span>
                       ) : (
                         <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                           <AlertCircle className="h-3 w-3 mr-1" />
                           Pending
                         </span>
                       )}
                     </td>
                     
                                                                 {/* File Size */}
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {file.file_size_mb ? `${file.file_size_mb.toFixed(2)} MB` : 'N/A'}
                      </td>
                      
                      {/* Actions */}
                     <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                       <div className="flex space-x-2">
                         <button
                           onClick={() => handleView(file)}
                           className="text-blue-600 hover:text-blue-900 flex items-center"
                           title="View file details"
                         >
                           <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                           </svg>
                           <span className="ml-1">View</span>
                         </button>
                         
                                                   {file.processed_flag && (
                            <button
                              onClick={() => handleDownload(file.file_id, file.filename)}
                              disabled={downloadingFiles.has(file.file_id) || token?.startsWith('demo-token-')}
                              className={`flex items-center ${
                                downloadingFiles.has(file.file_id) || token?.startsWith('demo-token-')
                                  ? 'text-gray-400 cursor-not-allowed'
                                  : 'text-green-600 hover:text-green-900'
                              }`}
                              title={
                                token?.startsWith('demo-token-') 
                                  ? 'Download not available in demo mode' 
                                  : downloadingFiles.has(file.file_id) 
                                    ? 'Downloading...' 
                                    : 'Download file'
                              }
                            >
                              {downloadingFiles.has(file.file_id) ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Download className="h-4 w-4" />
                              )}
                              <span className="ml-1">
                                {downloadingFiles.has(file.file_id) ? 'Downloading...' : 'Download'}
                              </span>
                            </button>
                          )}
                         
                         {hiddenFiles.has(file.file_id) ? (
                           <button
                             onClick={() => handleUnhide(file.file_id)}
                             className="text-green-600 hover:text-green-900 flex items-center"
                             title="Unhide file"
                           >
                             <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                             </svg>
                             <span className="ml-1">Unhide</span>
                           </button>
                         ) : (
                           <button
                             onClick={() => handleHide(file.file_id)}
                             className="text-red-600 hover:text-red-900 flex items-center"
                             title="Hide file"
                           >
                             <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                             </svg>
                             <span className="ml-1">Hide</span>
                           </button>
                         )}
                       </div>
                     </td>
                   </tr>
                 ))
               )}
             </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
