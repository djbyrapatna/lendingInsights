// src/pages/LoanEligibilityPage.tsx
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

interface EvaluationRecord {
  id: number;
  filename: string;
  evaluation_result: {
    applicantName: string;
    loan_eligibility_score: number;
    message: string;
    // other fields if needed...
  };
  created_at: string;
  // ... other fields if needed
}

const LoanEligibilityPage: React.FC = () => {
  const [evaluations, setEvaluations] = useState<EvaluationRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  // Helper function to compute loan recommendation based on the score.
  const computeLoanRecommendation = (score: number): string => {
    if (score > 10) return 'Eligible for loan';
    else if (score >= -20 && score <= 10) return 'Manual review recommended';
    else return 'Ineligible for loan';
  };

  // Fetch evaluations from backend API on component mount.
  useEffect(() => {
    const fetchEvaluations = async () => {
      try {
        // Replace with your actual API endpoint URL
        const response = await axios.get<EvaluationRecord[]>('http://127.0.0.1:8000/api/pdf/evaluations');
        console.log('Fetched evaluations:', response.data);
        setEvaluations(response.data);
        
      } catch (err: any) {
        console.error('Error fetching evaluations:', err);
        setError('Failed to fetch evaluations.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchEvaluations();
  }, []);

  if (loading) return <div>Loading evaluations...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Loan Eligibility</h1>
      <table style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid black', padding: '0.5rem' }}>Applicant Name</th>
            <th style={{ border: '1px solid black', padding: '0.5rem' }}>Loan Eligibility Score</th>
            <th style={{ border: '1px solid black', padding: '0.5rem' }}>Loan Recommendation</th>
            <th style={{ border: '1px solid black', padding: '0.5rem' }}>Data Warning</th>
            <th style={{ border: '1px solid black', padding: '0.5rem' }}>Metrics Page</th>
          </tr>
        </thead>
        <tbody>
          {evaluations.map((evalRec) => {
            const result = evalRec.evaluation_result;
            return (
              <tr key={evalRec.id}>
                <td style={{ border: '1px solid black', padding: '0.5rem' }}>
                  {result.applicantName}
                </td>
                <td style={{ border: '1px solid black', padding: '0.5rem' }}>
                {Math.trunc(result.loan_eligibility_score)}
                </td>
                <td style={{ border: '1px solid black', padding: '0.5rem' }}>
                  {computeLoanRecommendation(result.loan_eligibility_score)}
                </td>
                <td style={{ border: '1px solid black', padding: '0.5rem' }}>
                  {result.message}
                </td>
                <td style={{ border: '1px solid black', padding: '0.5rem' }}>
                  <Link to={`/metrics?evaluationId=${evalRec.id}`}>View Metrics</Link>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
export default LoanEligibilityPage;
