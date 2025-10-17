// components/FileUploader.jsx
import React, { useState, useRef } from "react";
import { uploadFiles, resetFiles } from "../api";
import "./FileUploader.css";

const FileUploader = ({ resetMode = false }) => {
  const [files, setFiles] = useState([]);
  const [message, setMessage] = useState({ text: "", type: "" });
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const fileIcons = {
    pdf: "📄",
    txt: "📝",
    docx: "📃",
    doc: "📃",
    csv: "📊",
    md: "📋",
  };

  const allowedTypes = [".pdf", ".txt", ".docx", ".doc", ".csv", ".md"];
  const maxFileSize = 10 * 1024 * 1024; // 10MB

  const validateFiles = (fileList) => {
    const invalidFiles = [];
    const validFiles = [];

    Array.from(fileList).forEach((file) => {
      const extension = "." + file.name.split(".").pop().toLowerCase();

      if (!allowedTypes.includes(extension)) {
        invalidFiles.push(`${file.name} - Invalid file type`);
      } else if (file.size > maxFileSize) {
        invalidFiles.push(`${file.name} - File too large (max 10MB)`);
      } else {
        validFiles.push(file);
      }
    });

    return { validFiles, invalidFiles };
  };

  const handleFilesChange = (e) => {
    const fileList = e.target.files;
    if (!fileList.length) return;

    const { validFiles, invalidFiles } = validateFiles(fileList);

    if (invalidFiles.length > 0) {
      setMessage({
        text: `Invalid files: ${invalidFiles.join(", ")}`,
        type: "error",
      });
    } else {
      setMessage({ text: "", type: "" });
    }

    setFiles(validFiles);
  };

  const handleSubmit = async () => {
    if (!files.length) {
      setMessage({ text: "Please select files to upload", type: "error" });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setMessage({ text: "", type: "" });

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    try {
      // Simulate progress for better UX - more realistic timing
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 80) {
            // Stop at 80% to wait for actual completion
            clearInterval(progressInterval);
            return 80;
          }
          return prev + 5;
        });
      }, 300);

      const response = resetMode
        ? await resetFiles(formData)
        : await uploadFiles(formData);

      clearInterval(progressInterval);
      setUploadProgress(100);

      setMessage({
        text: response.data.message,
        type: "success",
      });

      setFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      // Reset progress after success
      setTimeout(() => setUploadProgress(0), 2000);
    } catch (error) {
      console.error("Upload error:", error);
      setUploadProgress(0);
      setMessage({
        text:
          error.response?.data?.detail ||
          error.response?.data?.message ||
          "Error uploading files. Please try a smaller file.",
        type: "error",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length) {
      const { validFiles, invalidFiles } = validateFiles(droppedFiles);

      if (invalidFiles.length > 0) {
        setMessage({
          text: `Invalid files: ${invalidFiles.join(", ")}`,
          type: "error",
        });
      }

      setFiles(validFiles);
    }
  };

  const cancelUpload = () => {
    setIsUploading(false);
    setUploadProgress(0);
    setMessage({ text: "Upload cancelled", type: "warning" });
  };

  return (
    <div className="file-uploader-card">
      <div className="uploader-header">
        <h3>
          {resetMode ? "Reset Knowledge Base" : "Add Files to Knowledge Base"}
        </h3>
        <p>
          {resetMode
            ? "Replace all existing files with new ones"
            : "Add new files to the existing knowledge base"}
        </p>
      </div>

      <div className="uploader-body">
        <div className="file-input-wrapper">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFilesChange}
            accept=".pdf,.txt,.docx,.doc,.csv,.md"
            disabled={isUploading}
            className="file-input"
          />
          <div
            className="file-input-label"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path
                d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                stroke="currentColor"
                strokeWidth="2"
              />
              <polyline
                points="14,2 14,8 20,8"
                stroke="currentColor"
                strokeWidth="2"
              />
              <line
                x1="16"
                y1="13"
                x2="8"
                y2="13"
                stroke="currentColor"
                strokeWidth="2"
              />
              <line
                x1="16"
                y1="17"
                x2="8"
                y2="17"
                stroke="currentColor"
                strokeWidth="2"
              />
              <polyline
                points="10,9 9,9 8,9"
                stroke="currentColor"
                strokeWidth="2"
              />
            </svg>
            <span>Choose files or drag and drop</span>
            <small>PDF, TXT, DOC, DOCX, CSV, MD (max 10MB each)</small>
          </div>
        </div>

        {files.length > 0 && (
          <div className="file-list">
            <div className="file-list-header">
              <span>Selected Files ({files.length})</span>
              <button
                onClick={() => setFiles([])}
                className="clear-all-btn"
                disabled={isUploading}
              >
                Clear All
              </button>
            </div>
            {files.map((file, index) => (
              <div key={index} className="file-item">
                <div className="file-info">
                  <span className="file-icon">
                    {fileIcons[file.name.split(".").pop()] || "📁"}
                  </span>
                  <div className="file-details">
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  disabled={isUploading}
                  className="remove-file-btn"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        {isUploading && (
          <div className="upload-progress">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <div className="progress-controls">
              <span className="progress-text">
                {uploadProgress < 100
                  ? `Processing... ${uploadProgress}%`
                  : "Complete!"}
              </span>
              {uploadProgress < 100 && (
                <button onClick={cancelUpload} className="cancel-btn">
                  Cancel
                </button>
              )}
            </div>
            {uploadProgress >= 80 && uploadProgress < 100 && (
              <div className="processing-note">
                ⏳ Processing file content... This may take a moment for large
                files.
              </div>
            )}
          </div>
        )}

        {message.text && (
          <div className={`message ${message.type}`}>{message.text}</div>
        )}

        <button
          onClick={handleSubmit}
          disabled={isUploading || files.length === 0}
          className={`submit-btn ${resetMode ? "reset" : "upload"}`}
        >
          {isUploading ? (
            <>
              <div className="spinner"></div>
              {resetMode ? "Resetting..." : "Uploading..."}
            </>
          ) : resetMode ? (
            "Reset Knowledge Base"
          ) : (
            "Upload Files"
          )}
        </button>
      </div>
    </div>
  );
};

export default FileUploader;
