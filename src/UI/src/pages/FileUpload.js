import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Upload, 
  FileText, 
  Loader2,
  X
} from 'lucide-react';

const FileUpload = () => {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [formData, setFormData] = useState({
    engagement_name: '',
    date1: '',
    date2: '',
    date3: '',
    date4: '',
  });
  const [selectedFile, setSelectedFile] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      
      // Validate file type
      const validTypes = ['.xlsx', '.csv'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (!validTypes.includes(fileExtension)) {
        toast.error('Please select a valid XLSX or CSV file');
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
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv'],
      'application/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
    },
    multiple: false,
  });

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

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
        navigate('/dashboard');
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
          Upload and process your XLSX or CSV files with geospatial data
        </p>
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
                  Supports XLSX and CSV files up to 50MB
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
          <h2 className="text-lg font-medium text-gray-900 mb-4">Engagement Details</h2>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="engagement_name" className="block text-sm font-medium text-gray-700">
                Engagement Name *
              </label>
              <input
                type="text"
                id="engagement_name"
                name="engagement_name"
                required
                className="input-field mt-1"
                placeholder="Enter engagement name"
                value={formData.engagement_name}
                onChange={handleInputChange}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="date1" className="block text-sm font-medium text-gray-700">
                  Date 1 *
                </label>
                <input
                  type="date"
                  id="date1"
                  name="date1"
                  required
                  className="input-field mt-1"
                  value={formData.date1}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label htmlFor="date2" className="block text-sm font-medium text-gray-700">
                  Date 2 *
                </label>
                <input
                  type="date"
                  id="date2"
                  name="date2"
                  required
                  className="input-field mt-1"
                  value={formData.date2}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label htmlFor="date3" className="block text-sm font-medium text-gray-700">
                  Date 3 *
                </label>
                <input
                  type="date"
                  id="date3"
                  name="date3"
                  required
                  className="input-field mt-1"
                  value={formData.date3}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label htmlFor="date4" className="block text-sm font-medium text-gray-700">
                  Date 4 *
                </label>
                <input
                  type="date"
                  id="date4"
                  name="date4"
                  required
                  className="input-field mt-1"
                  value={formData.date4}
                  onChange={handleInputChange}
                />
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
            onClick={() => navigate('/dashboard')}
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
          <li>• Supported file formats: XLSX, CSV</li>
          <li>• Maximum file size: 50MB</li>
          <li>• All date fields are required</li>
          <li>• Files will be processed automatically after upload</li>
          <li>• You can download processed files from the dashboard</li>
        </ul>
      </div>
    </div>
  );
};

export default FileUpload;
