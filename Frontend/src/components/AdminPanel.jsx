// components/AdminPanel.jsx
import React from "react";
import FileUploader from "./FileUploader";
import "./AdminPanel.css";

const AdminPanel = () => {
  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h1>Knowledge Base Management</h1>
        <p>Upload and manage files for the AI assistant</p>
      </div>

      <div className="uploader-grid">
        <div className="uploader-section">
          <h3>Add Files</h3>
          <p>Upload new files to enhance the knowledge base</p>
          <FileUploader resetMode={false} />
        </div>

        <div className="uploader-section">
          <h3>Reset & Replace</h3>
          <p>Clear all existing files and upload new ones</p>
          <FileUploader resetMode={true} />
        </div>
      </div>

      <div className="admin-info">
        <h4>Supported File Types</h4>
        <div className="file-types">
          <span className="file-type-tag">PDF</span>
          <span className="file-type-tag">TXT</span>
          <span className="file-type-tag">DOC/DOCX</span>
          <span className="file-type-tag">CSV</span>
          <span className="file-type-tag">Markdown</span>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
