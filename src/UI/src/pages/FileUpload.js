import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Upload, 
  FileText, 
  Loader2,
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

const FileUpload = () => {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [formData, setFormData] = useState({
    engagement_name: '',
    date1: '2025-01-01', // Baseline Period Start - January 1st
    date2: '2025-03-31', // Baseline Period End - March 31st
    date3: '2025-07-01', // Current Period Start - July 1st
    date4: '2025-07-31', // Current Period End - July 31st
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [activeDatePicker, setActiveDatePicker] = useState(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  
  // Filter state
  const [filters, setFilters] = useState({
    state: 'Andhra Pradesh',
    district: 'Nellore',
    division: 'Rapur'
  });

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      
      // Validate file type
      const validTypes = ['.csv'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (!validTypes.includes(fileExtension)) {
        toast.error('Please select a valid CSV file');
        return;
      }
      
      // Validate file size (50MB limit)
      if (file.size > 50 * 1024 * 1024) {
        toast.error('File size must be less than 50MB');
        return;
      }
      
      setSelectedFile(file);
      toast.success('File selected successfully');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/csv': ['.csv'],
    },
    multiple: false,
  });

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // Format date from YYYY-MM-DD to DD/MM/YYYY in IST
  const formatDateForDisplay = (dateString) => {
    if (!dateString) return '';
    // Convert to IST timezone (UTC+5:30)
    const date = new Date(dateString + 'T00:00:00.000Z');
    const istDate = new Date(date.getTime() + (5.5 * 60 * 60 * 1000));
    const day = String(istDate.getUTCDate()).padStart(2, '0');
    const month = String(istDate.getUTCMonth() + 1).padStart(2, '0');
    const year = istDate.getUTCFullYear();
    return `${day}/${month}/${year}`;
  };

  // Copy text to clipboard
  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success('Date copied to clipboard!');
    } catch (err) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      toast.success('Date copied to clipboard!');
    }
  };

  // Custom Calendar Component
  const CustomCalendar = ({ fieldName, currentDate, onDateSelect, onClose }) => {
    const [selectedDate, setSelectedDate] = useState(currentDate ? new Date(currentDate) : new Date());
    const [displayMonth, setDisplayMonth] = useState(selectedDate);

    const getDaysInMonth = (date) => {
      const year = date.getFullYear();
      const month = date.getMonth();
      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0);
      const daysInMonth = lastDay.getDate();
      const startingDay = firstDay.getDay();
      
      const days = [];
      
      // Add empty cells for days before the first day of the month
      for (let i = 0; i < startingDay; i++) {
        days.push(null);
      }
      
      // Add days of the month
      for (let i = 1; i <= daysInMonth; i++) {
        days.push(new Date(year, month, i));
      }
      
      return days;
    };

    const handleDateClick = (date) => {
      if (date) {
        setSelectedDate(date);
        // Convert to IST timezone (UTC+5:30)
        const istDate = new Date(date.getTime() + (5.5 * 60 * 60 * 1000));
        const year = istDate.getUTCFullYear();
        const month = String(istDate.getUTCMonth() + 1).padStart(2, '0');
        const day = String(istDate.getUTCDate()).padStart(2, '0');
        const formattedDate = `${year}-${month}-${day}`;
        onDateSelect(fieldName, formattedDate);
        onClose();
      }
    };

    const goToPreviousMonth = () => {
      setDisplayMonth(new Date(displayMonth.getFullYear(), displayMonth.getMonth() - 1, 1));
    };

    const goToNextMonth = () => {
      setDisplayMonth(new Date(displayMonth.getFullYear(), displayMonth.getMonth() + 1, 1));
    };

    const days = getDaysInMonth(displayMonth);
    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];

    return (
      <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-50 p-3 min-w-[280px]">
        <div className="flex items-center justify-between mb-3">
          <button
            type="button"
            onClick={goToPreviousMonth}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <h3 className="text-sm font-medium">
            {monthNames[displayMonth.getMonth()]} {displayMonth.getFullYear()}
          </h3>
          <button
            type="button"
            onClick={goToNextMonth}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
        
        <div className="grid grid-cols-7 gap-1 text-xs">
          {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(day => (
            <div key={day} className="p-2 text-center text-gray-500 font-medium">
              {day}
            </div>
          ))}
          
          {days.map((day, index) => (
            <button
              key={index}
              type="button"
              onClick={() => handleDateClick(day)}
              disabled={!day}
              className={`p-2 text-center rounded hover:bg-blue-50 ${
                !day ? 'text-gray-300' : 'text-gray-700 hover:text-blue-600'
              } ${
                day && selectedDate && day.toDateString() === selectedDate.toDateString()
                  ? 'bg-blue-500 text-white hover:bg-blue-600'
                  : ''
              }`}
            >
              {day ? day.getDate() : ''}
            </button>
          ))}
        </div>
        
        <div className="flex justify-between mt-3 pt-3 border-t">
          <button
            type="button"
            onClick={() => handleDateClick(new Date())}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            Today
          </button>
          <button
            type="button"
            onClick={onClose}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  };

  const handleDateSelect = (fieldName, date) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: date
    }));
  };

  const toggleDatePicker = (fieldName) => {
    if (activeDatePicker === fieldName) {
      setActiveDatePicker(null);
    } else {
      setActiveDatePicker(fieldName);
    }
  };

  // Close date picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.date-picker-container')) {
        setActiveDatePicker(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      toast.error('Please select a file to upload');
      return;
    }

    // Validate required fields
    const requiredFields = ['engagement_name', 'date1', 'date2', 'date3', 'date4'];
    const missingFields = requiredFields.filter(field => !formData[field]);
    
    if (missingFields.length > 0) {
      toast.error(`Please fill in all required fields: ${missingFields.join(', ')}`);
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const uploadFormData = new FormData();
      uploadFormData.append('file', selectedFile);
      uploadFormData.append('engagement_name', formData.engagement_name);
      uploadFormData.append('date1', formData.date1);
      uploadFormData.append('date2', formData.date2);
      uploadFormData.append('date3', formData.date3);
      uploadFormData.append('date4', formData.date4);

      const response = await axios.post('/api/v1/files/upload', uploadFormData, {
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        },
      });

      if (response.data.status === 'success') {
        toast.success('File uploaded and processed successfully!');
        navigate('/dashboard', { state: { refreshDashboard: true } });
      }
    } catch (error) {
      console.error('Upload error:', error);
      const message = error.response?.data?.message || 'Upload failed. Please try again.';
      toast.error(message);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload File</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload and process your CSV files with geospatial data
        </p>
      </div>

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

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File Upload Area */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Select File</h2>
          
          {!selectedFile ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-primary-400 bg-primary-50'
                  : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div className="mt-4">
                <p className="text-sm text-gray-600">
                  {isDragActive
                    ? 'Drop the file here...'
                    : 'Drag and drop a file here, or click to select'}
                </p>
                                 <p className="text-xs text-gray-500 mt-1">
                   Supports CSV files up to 50MB
                 </p>
              </div>
            </div>
          ) : (
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <FileText className="h-8 w-8 text-primary-600 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-xs text-gray-500">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={removeFile}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Form Fields */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Project Details</h2>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="engagement_name" className="block text-sm font-medium text-gray-700">
                Project Name *
              </label>
              <input
                type="text"
                id="engagement_name"
                name="engagement_name"
                required
                className="input-field mt-1"
                placeholder="Enter project name"
                value={formData.engagement_name}
                onChange={handleInputChange}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Date 1 - Baseline Period Start */}
              <div className="date-picker-container relative">
                <label htmlFor="date1" className="block text-sm font-medium text-gray-700">
                  Baseline Period Start *
                </label>
                <div className="relative">
                  <input
                    type="text"
                    id="date1"
                    name="date1"
                    required
                    className="input-field mt-1 pr-10"
                    value={formData.date1 ? formatDateForDisplay(formData.date1) : ''}
                    placeholder="dd/mm/yyyy"
                    readOnly
                  />
                  <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
                    <button
                      type="button"
                      onClick={() => toggleDatePicker('date1')}
                      className="text-gray-400 hover:text-gray-600"
                      title="Select date"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </button>
                    <button
                      type="button"
                      onClick={() => copyToClipboard(formatDateForDisplay(formData.date1))}
                      className="text-gray-400 hover:text-gray-600"
                      title="Copy date"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                </div>
                {activeDatePicker === 'date1' && (
                  <CustomCalendar
                    fieldName="date1"
                    currentDate={formData.date1}
                    onDateSelect={handleDateSelect}
                    onClose={() => setActiveDatePicker(null)}
                  />
                )}
              </div>

              {/* Date 2 - Baseline Period End */}
              <div className="date-picker-container relative">
                <label htmlFor="date2" className="block text-sm font-medium text-gray-700">
                  Baseline Period End *
                </label>
                <div className="relative">
                  <input
                    type="text"
                    id="date2"
                    name="date2"
                    required
                    className="input-field mt-1 pr-10"
                    value={formData.date2 ? formatDateForDisplay(formData.date2) : ''}
                    placeholder="dd/mm/yyyy"
                    readOnly
                  />
                  <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
                    <button
                      type="button"
                      onClick={() => toggleDatePicker('date2')}
                      className="text-gray-400 hover:text-gray-600"
                      title="Select date"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </button>
                    <button
                      type="button"
                      onClick={() => copyToClipboard(formatDateForDisplay(formData.date2))}
                      className="text-gray-400 hover:text-gray-600"
                      title="Copy date"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                </div>
                {activeDatePicker === 'date2' && (
                  <CustomCalendar
                    fieldName="date2"
                    currentDate={formData.date2}
                    onDateSelect={handleDateSelect}
                    onClose={() => setActiveDatePicker(null)}
                  />
                )}
              </div>

              {/* Date 3 - Current Period Start */}
              <div className="date-picker-container relative">
                <label htmlFor="date3" className="block text-sm font-medium text-gray-700">
                  Current Period Start *
                </label>
                <div className="relative">
                  <input
                    type="text"
                    id="date3"
                    name="date3"
                    required
                    className="input-field mt-1 pr-10"
                    value={formData.date3 ? formatDateForDisplay(formData.date3) : ''}
                    placeholder="dd/mm/yyyy"
                    readOnly
                  />
                  <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
                    <button
                      type="button"
                      onClick={() => toggleDatePicker('date3')}
                      className="text-gray-400 hover:text-gray-600"
                      title="Select date"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </button>
                    <button
                      type="button"
                      onClick={() => copyToClipboard(formatDateForDisplay(formData.date3))}
                      className="text-gray-400 hover:text-gray-600"
                      title="Copy date"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                </div>
                {activeDatePicker === 'date3' && (
                  <CustomCalendar
                    fieldName="date3"
                    currentDate={formData.date3}
                    onDateSelect={handleDateSelect}
                    onClose={() => setActiveDatePicker(null)}
                  />
                )}
              </div>

              {/* Date 4 - Current Period End */}
              <div className="date-picker-container relative">
                <label htmlFor="date4" className="block text-sm font-medium text-gray-700">
                  Current Period End *
                </label>
                <div className="relative">
                  <input
                    type="text"
                    id="date4"
                    name="date4"
                    required
                    className="input-field mt-1 pr-10"
                    value={formData.date4 ? formatDateForDisplay(formData.date4) : ''}
                    placeholder="dd/mm/yyyy"
                    readOnly
                  />
                  <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
                    <button
                      type="button"
                      onClick={() => toggleDatePicker('date4')}
                      className="text-gray-400 hover:text-gray-600"
                      title="Select date"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </button>
                    <button
                      type="button"
                      onClick={() => copyToClipboard(formatDateForDisplay(formData.date4))}
                      className="text-gray-400 hover:text-gray-600"
                      title="Copy date"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                </div>
                {activeDatePicker === 'date4' && (
                  <CustomCalendar
                    fieldName="date4"
                    currentDate={formData.date4}
                    onDateSelect={handleDateSelect}
                    onClose={() => setActiveDatePicker(null)}
                  />
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Upload Progress */}
        {uploading && (
          <div className="card">
            <div className="flex items-center mb-4">
              <Loader2 className="h-5 w-5 animate-spin text-primary-600 mr-2" />
              <span className="text-sm font-medium text-gray-900">Uploading and processing...</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500 mt-2">{uploadProgress}% complete</p>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/dashboard', { state: { refreshDashboard: false } })}
            className="btn-secondary"
            disabled={uploading}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={uploading || !selectedFile}
            className="btn-primary flex items-center"
          >
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Upload & Process
              </>
            )}
          </button>
        </div>
      </form>

      {/* Instructions */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="text-sm font-medium text-blue-900 mb-2">Upload Instructions</h3>
                 <ul className="text-sm text-blue-800 space-y-1">
           <li>• Supported file formats: CSV only</li>
           <li>• Maximum file size: 50MB</li>
           <li>• All date fields are required and pre-filled with common periods</li>
           <li>• Click the calendar icon to change dates, copy icon to copy the full date</li>
           <li>• Dates are displayed in DD/MM/YYYY format</li>
           <li>• Files will be processed automatically after upload</li>
           <li>• You can download processed files from the dashboard</li>
         </ul>
      </div>
    </div>
  );
};

export default FileUpload;
