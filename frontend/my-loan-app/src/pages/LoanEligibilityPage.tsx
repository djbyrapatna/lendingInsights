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
}

const LoanEligibilityPage: React.FC = () => {
  const [evaluations, setEvaluations] = useState<EvaluationRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  // Filter state variables
  const [filterName, setFilterName] = useState<string>('');
  const [minScore, setMinScore] = useState<string>('');
  const [maxScore, setMaxScore] = useState<string>('');
  const [filterRecommendation, setFilterRecommendation] = useState<string>('');

  // Sorting state variables
  const [sortColumn, setSortColumn] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Helper to compute loan recommendation based on score.
  const computeLoanRecommendation = (score: number): string => {
    if (score > 10) return 'Eligible for loan';
    else if (score >= -20 && score <= 10) return 'Manual review recommended';
    else return 'Ineligible for loan';
  };

  useEffect(() => {
    const fetchEvaluations = async () => {
      try {
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

  // Filtering logic:
  const filteredEvaluations = evaluations.filter((evalRec) => {
    const result = evalRec.evaluation_result;
    const matchesName = result.applicantName.toLowerCase().includes(filterName.toLowerCase());
    const score = result.loan_eligibility_score;
    const minOk = minScore === '' || score >= Number(minScore);
    const maxOk = maxScore === '' || score <= Number(maxScore);
    const recommendation = computeLoanRecommendation(score);
    const matchesRec =
      filterRecommendation === '' || recommendation.toLowerCase().includes(filterRecommendation.toLowerCase());
    return matchesName && minOk && maxOk && matchesRec;
  });

  // Sorting logic:
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      // Toggle direction if same column is clicked again.
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  // Apply sorting to the filtered evaluations.
  const sortedEvaluations = filteredEvaluations.sort((a, b) => {
    let aVal: any, bVal: any;
    if (sortColumn === 'applicantName') {
      aVal = a.evaluation_result.applicantName.toLowerCase();
      bVal = b.evaluation_result.applicantName.toLowerCase();
    } else if (sortColumn === 'loan_eligibility_score') {
      aVal = a.evaluation_result.loan_eligibility_score;
      bVal = b.evaluation_result.loan_eligibility_score;
    } else if (sortColumn === 'loanRecommendation') {
      // For recommendation, sort by the underlying score.
      aVal = a.evaluation_result.loan_eligibility_score;
      bVal = b.evaluation_result.loan_eligibility_score;
    } else {
      return 0; // No sorting if sortColumn is not set.
    }
    if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  if (loading) return <div>Loading evaluations...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Loan Eligibility</h1>
      
      {/* Filters */}
      <div style={{ marginBottom: '1rem' }}>
        <label>
          Applicant Name:{' '}
          <input 
            type="text" 
            value={filterName} 
            onChange={(e) => setFilterName(e.target.value)} 
          />
        </label>
        <label style={{ marginLeft: '1rem' }}>
          Min Score:{' '}
          <input 
            type="number" 
            value={minScore} 
            onChange={(e) => setMinScore(e.target.value)} 
            style={{ width: '80px' }}
          />
        </label>
        <label style={{ marginLeft: '1rem' }}>
          Max Score:{' '}
          <input 
            type="number" 
            value={maxScore} 
            onChange={(e) => setMaxScore(e.target.value)} 
            style={{ width: '80px' }}
          />
        </label>
        <label style={{ marginLeft: '1rem' }}>
          Loan Recommendation:{' '}
          <select 
            value={filterRecommendation} 
            onChange={(e) => setFilterRecommendation(e.target.value)}
          >
            <option value="">All</option>
            <option value="Eligible">Eligible for loan</option>
            <option value="Manual">Manual review recommended</option>
            <option value="Ineligible">Ineligible for loan</option>
          </select>
        </label>
      </div>

      {/* Table */}
      <table style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>
            <th 
              style={{ border: '1px solid black', padding: '0.5rem', cursor: 'pointer' }}
              onClick={() => handleSort('applicantName')}
            >
              Applicant Name {sortColumn === 'applicantName' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
            </th>
            <th 
              style={{ border: '1px solid black', padding: '0.5rem', cursor: 'pointer' }}
              onClick={() => handleSort('loan_eligibility_score')}
            >
              Loan Eligibility Score {sortColumn === 'loan_eligibility_score' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
            </th>
            <th 
              style={{ border: '1px solid black', padding: '0.5rem', cursor: 'pointer' }}
              onClick={() => handleSort('loanRecommendation')}
            >
              Loan Recommendation {sortColumn === 'loanRecommendation' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
            </th>
            <th style={{ border: '1px solid black', padding: '0.5rem' }}>Data Warning</th>
            <th style={{ border: '1px solid black', padding: '0.5rem' }}>Metrics Page</th>
          </tr>
        </thead>
        <tbody>
          {sortedEvaluations.length > 0 ? (
            sortedEvaluations.map((evalRec) => {
              const result = evalRec.evaluation_result;
              return (
                <tr key={evalRec.id}>
                  <td style={{ border: '1px solid black', padding: '0.5rem' }}>{result.applicantName}</td>
                  <td style={{ border: '1px solid black', padding: '0.5rem' }}>
                    {Math.trunc(result.loan_eligibility_score)}
                  </td>
                  <td style={{ border: '1px solid black', padding: '0.5rem' }}>
                    {computeLoanRecommendation(result.loan_eligibility_score)}
                  </td>
                  <td style={{ border: '1px solid black', padding: '0.5rem' }}>{result.message}</td>
                  <td style={{ border: '1px solid black', padding: '0.5rem' }}>
                    <Link to={`/metrics?evaluationId=${evalRec.id}`}>View Metrics</Link>
                  </td>
                </tr>
              );
            })
          ) : (
            <tr>
              <td colSpan={5} style={{ textAlign: 'center', padding: '1rem' }}>
                No records match the filter criteria.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default LoanEligibilityPage;
