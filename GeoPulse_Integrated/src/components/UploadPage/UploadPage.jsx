import React, { useState } from 'react';
import { Upload, FileText, X, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useNotification } from '../common/NotificationSystem';
import { fileService } from '../../services/api';
import './UploadPage.css';

const UploadPage = () => {
  const navigate = useNavigate();
  const { showNotification } = useNotification();

  const [selectedFile, setSelectedFile] = useState(null);
  const [engagementName, setEngagementName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type (CSV only for now)
      if (!file.name.toLowerCase().endsWith('.csv')) {
        showNotification('Please select a CSV file', 'error');
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        showNotification('File size must be less than 10MB', 'error');
        return;
      }

      setSelectedFile(file);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      handleFileSelect({ target: { files: [file] } });
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const removeFile = () => {
    setSelectedFile(null);
  };

  const handleUpload = async () => {
    if (!selectedFile || !engagementName.trim()) {
      showNotification('Please select a file and enter an engagement name', 'error');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      await fileService.uploadFile(selectedFile, engagementName.trim());

      clearInterval(progressInterval);
      setUploadProgress(100);

      showNotification('File uploaded successfully!', 'success');

      // Reset form
      setSelectedFile(null);
      setEngagementName('');

      // Navigate back to dashboard after a short delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);

    } catch (error) {
      console.error('Upload error:', error);
      showNotification(error.message || 'Upload failed. Please try again.', 'error');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="upload-container">
      <div className="upload-header">
        <button
          className="back-btn"
          onClick={() => navigate('/dashboard')}
        >
          ← Back to Dashboard
        </button>
        <h1>Upload File</h1>
      </div>

      <div className="upload-card">
        <div className="upload-form">
          {/* Engagement Name Input */}
          <div className="form-group">
            <label htmlFor="engagementName">Engagement Name</label>
            <input
              type="text"
              id="engagementName"
              value={engagementName}
              onChange={(e) => setEngagementName(e.target.value)}
              placeholder="Enter engagement name"
              className="form-input"
              disabled={isUploading}
            />
          </div>

          {/* File Upload Area */}
          <div
            className={`upload-area ${selectedFile ? 'has-file' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            {!selectedFile ? (
              <>
                <Upload size={48} />
                <h3>Drop your CSV file here</h3>
                <p>or click to browse</p>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileSelect}
                  className="file-input"
                  disabled={isUploading}
                />
                <div className="upload-info">
                  <p>Supported format: CSV</p>
                  <p>Maximum file size: 10MB</p>
                </div>
              </>
            ) : (
              <div className="selected-file">
                <div className="file-info">
                  <FileText size={32} />
                  <div className="file-details">
                    <h4>{selectedFile.name}</h4>
                    <p>{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
                {!isUploading && (
                  <button
                    className="remove-file-btn"
                    onClick={removeFile}
                  >
                    <X size={20} />
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Upload Progress */}
          {isUploading && (
            <div className="upload-progress">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p>Uploading... {uploadProgress}%</p>
            </div>
          )}

          {/* Upload Button */}
          <button
            className={`upload-btn ${isUploading ? 'uploading' : ''}`}
            onClick={handleUpload}
            disabled={!selectedFile || !engagementName.trim() || isUploading}
          >
            {isUploading ? (
              <>
                <div className="spinner"></div>
                Uploading...
              </>
            ) : uploadProgress === 100 ? (
              <>
                <CheckCircle size={20} />
                Upload Complete
              </>
            ) : (
              <>
                <Upload size={20} />
                Upload File
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;