// src/pages/UploadPage.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FileUpload from '../components/FileUpload';
//import { Link } from 'react-router-dom';

interface EvaluationRecord {
  id: number;
  filename: string;
  evaluation_result: {
    applicantName: string;
    loan_eligibility_score: number;
    message: string;
    // ... other fields if any
  };
  created_at: string;
}


const UploadPage: React.FC = () => {
  const [applicants, setApplicants] = useState<EvaluationRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  // Fetch the list of applicants from the backend
  useEffect(() => {
    const fetchApplicants = async () => {
      try {
        const response = await axios.get<EvaluationRecord[]>('http://127.0.0.1:8000/api/pdf/evaluations');
        setApplicants(response.data);
      } catch (err: any) {
        console.error("Error fetching applicants:", err);
        setError("Failed to fetch applicants.");
      } finally {
        setLoading(false);
      }
    };

    fetchApplicants();
  }, []);



  const handleUploadResult = (data: any) => {
    // Handle the uploaded data (e.g., route to a metrics page or store in global state)
    console.log("Upload result:", data);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Upload PDF</h1>
      <p>Please upload your bank transaction PDF to analyze loan eligibility.</p>
      <FileUpload onUpload={handleUploadResult} />
    

     {/* Spacer */}
     <div style={{ margin: '2rem 0' }}></div>

     <h2>All Applicants</h2>

     {/* Loading State */}
     {loading && <p>Loading applicants...</p>}

     {/* Error State */}
     {error && <p style={{ color: 'red' }}>{error}</p>}

     {/* Applicants Table */}
     {!loading && !error && applicants.length > 0 && (
       <table style={{ borderCollapse: 'collapse', width: '100%' }}>
         <thead>
           <tr>
             <th style={{ border: '1px solid #ddd', padding: '8px' }}>Applicant Name</th>
             <th style={{ border: '1px solid #ddd', padding: '8px' }}>Download PDF</th>
           </tr>
         </thead>
         <tbody>
           {applicants.map((applicant) => (
             <tr key={applicant.id}>
               <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                 {applicant.evaluation_result.applicantName}
               </td>
               <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                 <a 
                   href={`http://127.0.0.1:8000/api/pdf/download/${applicant.filename}`} 
                   download
                   target="_blank"
                   rel="noopener noreferrer"
                   style={{ color: '#007bff', textDecoration: 'none' }}
                 >
                   Download PDF
                 </a>
               </td>
             </tr>
           ))}
         </tbody>
       </table>
     )}

     {/* No Applicants Message */}
     {!loading && !error && applicants.length === 0 && (
       <p>No applicants found. Please upload a PDF to add an applicant.</p>
     )}
   </div>
   
  );
};

export default UploadPage;
