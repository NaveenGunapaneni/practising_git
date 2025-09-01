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

// Custom Dropdown Component with rounded corners
const CustomDropdown = ({ id, name, value, onChange, options, required }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedOption, setSelectedOption] = useState(
    options.find(opt => opt.value === value) || options[0]
  );

  const handleSelect = (option) => {
    if (!option.disabled) {
      setSelectedOption(option);
      onChange(option.value);
      setIsOpen(false);
    }
  };

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.custom-dropdown-container')) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="custom-dropdown-container relative">
      <div
        className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm bg-white cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent flex items-center justify-between"
        onClick={toggleDropdown}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggleDropdown();
          }
        }}
      >
        <span className={selectedOption.disabled ? 'text-gray-500' : 'text-gray-900'}>
          {selectedOption.label}
        </span>
        <svg
          className={`h-5 w-5 text-gray-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
          {options.map((option, index) => (
            <div
              key={index}
              className={`px-3 py-2 cursor-pointer transition-colors duration-150 ${option.disabled
                ? 'text-white cursor-not-allowed bg-primary-600'
                : 'text-gray-900 hover:bg-blue-50 hover:text-blue-600'
                } ${index === 0 ? 'rounded-t-lg' : ''
                } ${index === options.length - 1 ? 'rounded-b-lg' : ''
                }`}
              onClick={() => handleSelect(option)}
            >
              {option.label}
            </div>
          ))}
        </div>
      )}

      {/* Hidden input for form submission */}
      <input
        type="hidden"
        id={id}
        name={name}
        value={value}
        required={required}
      />
    </div>
  );
};

const FileUpload = () => {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [formData, setFormData] = useState({
    engagement_name: '',
    acreage: '', // Select Acreage - empty by default
    baseline_date: '2024-08-10', // Baseline Date - 10 August 2024
    target_date: '2025-08-10', // Target Date - 10 August 2025
  });
  
  // Separate state for date display values to allow manual typing
  const [dateDisplayValues, setDateDisplayValues] = useState({
    baseline_date: '10/08/2024',
    target_date: '10/08/2025'
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [activeDatePicker, setActiveDatePicker] = useState(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());

  // Filter state
  const [filters, setFilters] = useState({
    state: 'Andhra Pradesh', // Default to Andhra Pradesh
    district: 'Nellore', // Default to Nellore
    division: 'Rapur' // Default to Rapur
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

  // Handle date input changes for manual typing
  const handleDateInputChange = (e) => {
    const { name, value } = e.target;
    
    // Update display value immediately for typing
    setDateDisplayValues(prev => ({
      ...prev,
      [name]: value
    }));

    // Try to parse and validate the date if it matches DD/MM/YYYY format
    const dateRegex = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/;
    const match = value.match(dateRegex);
    
    if (match) {
      const day = parseInt(match[1], 10);
      const month = parseInt(match[2], 10);
      const year = parseInt(match[3], 10);
      
      // Validate date
      if (day >= 1 && day <= 31 && month >= 1 && month <= 12 && year >= 1900) {
        const date = new Date(year, month - 1, day);
        if (date.getDate() === day && date.getMonth() === month - 1) {
          // Valid date - convert to backend format (YYYY-MM-DD)
          const formattedDate = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
          setFormData(prev => ({
            ...prev,
            [name]: formattedDate
          }));
        }
      }
    }
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
    const [showYearSelector, setShowYearSelector] = useState(false);
    const [showMonthSelector, setShowMonthSelector] = useState(false);
    const [manualInput, setManualInput] = useState('');
    const [showManualInput, setShowManualInput] = useState(false);

    // Get yesterday's date for target date restriction
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);

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

    const isDateDisabled = (date) => {
      if (!date) return true;

      // For target date, disable today and future dates
      if (fieldName === 'target_date') {
        return date > yesterday;
      }

      return false;
    };

    const handleDateClick = (date) => {
      if (date && !isDateDisabled(date)) {
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

    const handleYearChange = (year) => {
      setDisplayMonth(new Date(year, displayMonth.getMonth(), 1));
      setShowYearSelector(false);
    };

    const handleMonthChange = (monthIndex) => {
      setDisplayMonth(new Date(displayMonth.getFullYear(), monthIndex, 1));
      setShowMonthSelector(false);
    };

    const handleManualDateSubmit = () => {
      // Parse manual input (dd/mm/yyyy format)
      const dateRegex = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/;
      const match = manualInput.match(dateRegex);

      if (match) {
        const day = parseInt(match[1], 10);
        const month = parseInt(match[2], 10) - 1; // Month is 0-indexed
        const year = parseInt(match[3], 10);

        const inputDate = new Date(year, month, day);

        // Validate the date
        if (inputDate.getDate() === day &&
          inputDate.getMonth() === month &&
          inputDate.getFullYear() === year &&
          !isDateDisabled(inputDate)) {

          setSelectedDate(inputDate);
          setDisplayMonth(inputDate);

          // Format for backend (YYYY-MM-DD)
          const formattedDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
          onDateSelect(fieldName, formattedDate);
          onClose();
        } else {
          alert('Please enter a valid date in DD/MM/YYYY format');
        }
      } else {
        alert('Please enter date in DD/MM/YYYY format');
      }
    };

    const generateYearOptions = () => {
      const currentYear = new Date().getFullYear();
      const years = [];
      for (let i = currentYear - 50; i <= currentYear + 10; i++) {
        years.push(i);
      }
      return years;
    };

    const days = getDaysInMonth(displayMonth);
    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];

    return (
      <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-50 p-3 min-w-[320px]">
        {/* Manual Input Section */}
        {showManualInput ? (
          <div className="mb-3 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <input
                type="text"
                placeholder="DD/MM/YYYY"
                value={manualInput}
                onChange={(e) => setManualInput(e.target.value)}
                className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleManualDateSubmit();
                  }
                }}
              />
              <button
                type="button"
                onClick={handleManualDateSubmit}
                className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Set
              </button>
            </div>
            <button
              type="button"
              onClick={() => {
                setShowManualInput(false);
                setManualInput('');
              }}
              className="text-xs text-gray-500 hover:text-gray-700"
            >
              ← Back to calendar
            </button>
          </div>
        ) : (
          <>
            {/* Header with navigation */}
            <div className="flex items-center justify-between mb-3">
              <button
                type="button"
                onClick={goToPreviousMonth}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={() => setShowMonthSelector(!showMonthSelector)}
                  className="text-sm font-medium text-blue-600 hover:text-blue-800 px-2 py-1 rounded hover:bg-blue-50"
                >
                  {monthNames[displayMonth.getMonth()]}
                </button>
                <button
                  type="button"
                  onClick={() => setShowYearSelector(!showYearSelector)}
                  className="text-sm font-medium text-blue-600 hover:text-blue-800 px-2 py-1 rounded hover:bg-blue-50"
                >
                  {displayMonth.getFullYear()}
                </button>
              </div>
              <button
                type="button"
                onClick={goToNextMonth}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>

            {/* Month Selector */}
            {showMonthSelector && (
              <div className="mb-3 grid grid-cols-3 gap-1 p-2 border border-gray-200 rounded">
                {monthNames.map((month, index) => (
                  <button
                    key={month}
                    type="button"
                    onClick={() => handleMonthChange(index)}
                    className={`px-2 py-1 text-xs text-center hover:bg-blue-50 rounded ${index === displayMonth.getMonth() ? 'bg-blue-100 text-blue-700' : ''
                      }`}
                  >
                    {month.substring(0, 3)}
                  </button>
                ))}
              </div>
            )}

            {/* Year Selector */}
            {showYearSelector && (
              <div className="mb-3 max-h-32 overflow-y-auto border border-gray-200 rounded">
                {generateYearOptions().map(year => (
                  <button
                    key={year}
                    type="button"
                    onClick={() => handleYearChange(year)}
                    className={`w-full px-3 py-1 text-sm text-left hover:bg-blue-50 ${year === displayMonth.getFullYear() ? 'bg-blue-100 text-blue-700' : ''
                      }`}
                  >
                    {year}
                  </button>
                ))}
              </div>
            )}

            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-1 text-xs">
              {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(day => (
                <div key={day} className="p-2 text-center text-gray-500 font-medium">
                  {day}
                </div>
              ))}

              {days.map((day, index) => {
                const disabled = isDateDisabled(day);
                return (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleDateClick(day)}
                    disabled={disabled}
                    className={`p-2 text-center rounded ${disabled
                      ? 'text-gray-300 cursor-not-allowed'
                      : 'hover:bg-blue-50 text-gray-700 hover:text-blue-600'
                      } ${day && selectedDate && day.toDateString() === selectedDate.toDateString()
                        ? 'bg-blue-500 text-white hover:bg-blue-600'
                        : ''
                      }`}
                  >
                    {day ? day.getDate() : ''}
                  </button>
                );
              })}
            </div>
          </>
        )}

        {/* Footer */}
        <div className="flex justify-between items-center mt-3 pt-3 border-t">
          <div className="flex space-x-2">
            {fieldName !== 'target_date' && (
              <button
                type="button"
                onClick={() => handleDateClick(new Date())}
                className="text-xs text-blue-600 hover:text-blue-800"
              >
                Today
              </button>
            )}
            {fieldName === 'target_date' && (
              <button
                type="button"
                onClick={() => handleDateClick(yesterday)}
                className="text-xs text-blue-600 hover:text-blue-800"
              >
                Yesterday
              </button>
            )}
            {!showManualInput && (
              <button
                type="button"
                onClick={() => setShowManualInput(true)}
                className="text-xs text-green-600 hover:text-green-800"
              >
                Type Date
              </button>
            )}
          </div>
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
    
    // Also update display value when calendar is used
    const displayDate = formatDateForDisplay(date);
    setDateDisplayValues(prev => ({
      ...prev,
      [fieldName]: displayDate
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
    const requiredFields = ['engagement_name', 'acreage', 'baseline_date', 'target_date'];
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
      uploadFormData.append('acreage', formData.acreage);
      uploadFormData.append('baseline_date', formData.baseline_date);
      uploadFormData.append('target_date', formData.target_date);

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
            <label htmlFor="state" className="block text-sm font-medium text-gray-700">
              Select State *
            </label>
            <CustomDropdown
              id="state"
              name="state"
              value={filters.state}
              onChange={(value) => setFilters(prev => ({ ...prev, state: value }))}
              options={[
                { value: '', label: 'Select state', disabled: true },
                { value: 'Andhra Pradesh', label: 'Andhra Pradesh' },
                { value: 'Telangana', label: 'Telangana' },
                { value: 'Karnataka', label: 'Karnataka' },
                { value: 'Tamil Nadu', label: 'Tamil Nadu' },
                { value: 'Kerala', label: 'Kerala' }
              ]}
              required
            />
          </div>

          {/* District Filter */}
          <div>
            <label htmlFor="district" className="block text-sm font-medium text-gray-700">
              Select District *
            </label>
            <CustomDropdown
              id="district"
              name="district"
              value={filters.district}
              onChange={(value) => setFilters(prev => ({ ...prev, district: value }))}
              options={[
                { value: '', label: 'Select district', disabled: true },
                { value: 'Nellore', label: 'Nellore' },
                { value: 'Visakhapatnam', label: 'Visakhapatnam' },
                { value: 'Vijayawada', label: 'Vijayawada' },
                { value: 'Guntur', label: 'Guntur' },
                { value: 'Kurnool', label: 'Kurnool' },
                { value: 'Kakinada', label: 'Kakinada' },
                { value: 'Kadapa', label: 'Kadapa' },
                { value: 'Tirupati', label: 'Tirupati' },
                { value: 'Anantapuramu', label: 'Anantapuramu' },
                { value: 'Vizianagaram', label: 'Vizianagaram' },
                { value: 'Eluru', label: 'Eluru' },
                { value: 'Nandyal', label: 'Nandyal' },
                { value: 'Ongole', label: 'Ongole' },
                { value: 'Adoni', label: 'Adoni' },
                { value: 'Madanapalle', label: 'Madanapalle' },
                { value: 'Machilipatnam', label: 'Machilipatnam' },
                { value: 'Tenali', label: 'Tenali' },
                { value: 'Proddatur', label: 'Proddatur' },
                { value: 'Chittoor', label: 'Chittoor' },
                { value: 'Hindupur', label: 'Hindupur' },
                { value: 'Srikakulam', label: 'Srikakulam' },
                { value: 'Bhimavaram', label: 'Bhimavaram' },
                { value: 'Tadepalligudem', label: 'Tadepalligudem' }
              ]}
              required
            />
          </div>

          {/* Division Filter */}
          <div>
            <label htmlFor="division" className="block text-sm font-medium text-gray-700">
              Select Division *
            </label>
            <CustomDropdown
              id="division"
              name="division"
              value={filters.division}
              onChange={(value) => setFilters(prev => ({ ...prev, division: value }))}
              options={[
                { value: '', label: 'Select division', disabled: true },
                { value: 'Rapur', label: 'Rapur' },
                { value: 'Alluri Sitharama Raju', label: 'Alluri Sitharama Raju' },
                { value: 'Anakapalli', label: 'Anakapalli' },
                { value: 'Anantapuramu', label: 'Anantapuramu' },
                { value: 'Annamayya', label: 'Annamayya' },
                { value: 'Bapatla', label: 'Bapatla' },
                { value: 'Chittoor', label: 'Chittoor' },
                { value: 'East Godavari', label: 'East Godavari' },
                { value: 'Eluru', label: 'Eluru' },
                { value: 'Guntur', label: 'Guntur' },
                { value: 'Kakinada', label: 'Kakinada' },
                { value: 'Krishna', label: 'Krishna' },
                { value: 'Kurnool', label: 'Kurnool' },
                { value: 'Nandyal', label: 'Nandyal' },
                { value: 'Nellore', label: 'Nellore' },
                { value: 'NTR', label: 'NTR' },
                { value: 'Palnadu', label: 'Palnadu' },
                { value: 'Prakasam', label: 'Prakasam' },
                { value: 'Srikakulam', label: 'Srikakulam' },
                { value: 'Sri Sathya Sai', label: 'Sri Sathya Sai' },
                { value: 'Tirupati', label: 'Tirupati' }
              ]}
              required
            />
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
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragActive
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

            <div>
              <label htmlFor="acreage" className="block text-sm font-medium text-gray-700">
                Plot Size *
              </label>
              <CustomDropdown
                id="acreage"
                name="acreage"
                value={formData.acreage}
                onChange={(value) => setFormData(prev => ({ ...prev, acreage: value }))}
                options={[
                  { value: '', label: 'Select plot size', disabled: true },
                  { value: 'as is', label: 'as is' },
                  { value: '0.25 acre', label: '0.25 acre' },
                  { value: '1 acre', label: '1 acre' }
                ]}
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Baseline Date */}
              <div className="date-picker-container relative">
                <label htmlFor="baseline_date" className="block text-sm font-medium text-gray-700">
                  Baseline Date *
                </label>
                <div className="relative">
                  <input
                    type="text"
                    id="baseline_date"
                    name="baseline_date"
                    required
                    className="input-field mt-1 pr-10"
                    value={dateDisplayValues.baseline_date}
                    placeholder="dd/mm/yyyy"
                    onChange={handleDateInputChange}
                  />
                  <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
                    <button
                      type="button"
                      onClick={() => toggleDatePicker('baseline_date')}
                      className="text-gray-400 hover:text-gray-600"
                      title="Select date"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </button>
                    <button
                      type="button"
                      onClick={() => copyToClipboard(formatDateForDisplay(formData.baseline_date))}
                      className="text-gray-400 hover:text-gray-600"
                      title="Copy date"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                </div>
                {activeDatePicker === 'baseline_date' && (
                  <CustomCalendar
                    fieldName="baseline_date"
                    currentDate={formData.baseline_date}
                    onDateSelect={handleDateSelect}
                    onClose={() => setActiveDatePicker(null)}
                  />
                )}
              </div>

              {/* Target Date */}
              <div className="date-picker-container relative">
                <label htmlFor="target_date" className="block text-sm font-medium text-gray-700">
                  Target Date *
                </label>
                <div className="relative">
                  <input
                    type="text"
                    id="target_date"
                    name="target_date"
                    required
                    className="input-field mt-1 pr-10"
                    value={dateDisplayValues.target_date}
                    placeholder="dd/mm/yyyy"
                    onChange={handleDateInputChange}
                  />
                  <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
                    <button
                      type="button"
                      onClick={() => toggleDatePicker('target_date')}
                      className="text-gray-400 hover:text-gray-600"
                      title="Select date"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </button>
                    <button
                      type="button"
                      onClick={() => copyToClipboard(formatDateForDisplay(formData.target_date))}
                      className="text-gray-400 hover:text-gray-600"
                      title="Copy date"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                </div>
                {activeDatePicker === 'target_date' && (
                  <CustomCalendar
                    fieldName="target_date"
                    currentDate={formData.target_date}
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
