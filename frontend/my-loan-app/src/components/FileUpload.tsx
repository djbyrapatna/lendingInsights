// src/components/FileUpload.tsx
import React, { useState } from 'react';
import { uploadPDF } from '../services/api';

interface FileUploadProps {
  onUpload: (data: any) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUpload }) => {
  const [file, setFile] = useState<File | null>(null);
  const [applicantName, setApplicantName] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
    }
  };

  const handleApplicantNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setApplicantName(event.target.value);
  };


  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await uploadPDF(file, applicantName);
      onUpload(data);
    } catch (err) {
      setError("Upload failed.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <br />
      <input
        type="text"
        placeholder="Enter applicant name"
        value={applicantName}
        onChange={handleApplicantNameChange}
      />
      <br />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>
      {error && <div style={{ color: "red" }}>{error}</div>}
    </div>
  );
};
export default FileUpload;
