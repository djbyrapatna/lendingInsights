// src/pages/UploadPage.tsx
import React from 'react';
import FileUpload from '../components/FileUpload';

const UploadPage: React.FC = () => {
  const handleUploadResult = (data: any) => {
    // Handle the uploaded data (e.g., route to a metrics page or store in global state)
    console.log("Upload result:", data);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Upload PDF</h1>
      <p>Please upload your bank transaction PDF to analyze loan eligibility.</p>
      <FileUpload onUpload={handleUploadResult} />
    </div>
  );
};

export default UploadPage;
