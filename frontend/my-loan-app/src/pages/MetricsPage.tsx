// src/pages/MetricsPage.tsx
import React, { useEffect, useState } from 'react';
//import { Link } from 'react-router-dom';
import axios from 'axios';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

interface Metrics {
  starting_balance: number;
  ending_balance: number;
  min_balance: number;
  total_income: number;
  total_expenses: number;
  net_cash_flow: number;
  [key: string]: any; // For other dynamic metrics
}

interface Transaction {
  Date: string | null;
  "Transaction Description": string;
  Debit: number | null;
  Credit: number | null;
  Balance: number;
  Category: string;
}
interface EvaluationResult {
  applicantName: string;
  loan_eligibility_score: number;
  message: string;
  metrics?: Metrics;
  transactions?: Transaction[];
}

interface EvaluationRecord {
  id: number;
  filename: string;
  evaluation_result: EvaluationResult;
  created_at: string;
}

const defaultMetrics: Metrics = {
  starting_balance: 0,
  ending_balance: 0,
  min_balance: 0,
  total_income: 0,
  total_expenses: 0,
  net_cash_flow: 0,
  // add any additional required metrics properties here
};


const MetricsPage: React.FC = () => {
  const [evaluations, setEvaluations] = useState<EvaluationRecord[]>([]);
  const [selectedEvaluation, setSelectedEvaluation] = useState<EvaluationRecord | null>(null);
  const [filterName, setFilterName] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  // Helper to compute recommendation based on score.
  const computeLoanRecommendation = (score: number): string => {
    if (score > 10) return 'Eligible for loan';
    else if (score >= -20 && score <= 10) return 'Manual review recommended';
    else return 'Ineligible for loan';
  };

  // Fetch evaluations from the backend
  useEffect(() => {
    const fetchEvaluations = async () => {
      try {
        const response = await axios.get<EvaluationRecord[]>('http://127.0.0.1:8000/api/pdf/evaluations');
        console.log('Fetched evaluations:', response.data);
        setEvaluations(response.data);
        // Set the first evaluation as selected if available.
        if (response.data.length > 0) {
          setSelectedEvaluation(response.data[0]);
        }
      } catch (err: any) {
        console.error('Error fetching evaluations:', err);
        setError('Failed to fetch evaluations.');
      } finally {
        setLoading(false);
      }
    };
    fetchEvaluations();
  }, []);

  // Filter evaluations based on applicant name.
  const filteredEvaluations = evaluations.filter((evalRec) =>
    evalRec.evaluation_result.applicantName.toLowerCase().includes(filterName.toLowerCase())
  );

  // Data for charts. We'll use the transactions array.
  const balanceData = selectedEvaluation?.evaluation_result.transactions
    ? selectedEvaluation.evaluation_result.transactions.map((tx, i) => ({
        time: tx.Date ? new Date(tx.Date).toLocaleDateString() : `T${i + 1}`,
        balance: tx.Balance !== undefined ? Number(tx.Balance) : 0,
      }))
    : [];
    console.log('Balance Data:', balanceData);
  // Expenses data: only transactions with Debit values.
  const expensesData = selectedEvaluation?.evaluation_result.transactions
    ? selectedEvaluation.evaluation_result.transactions
        .filter((tx: Transaction) => tx.Debit !== null)
        .map((tx: Transaction, i: number) => ({
          time: tx.Date ? new Date(tx.Date).toLocaleDateString() : `T${i + 1}`,
          expense: tx.Debit,
        }))
    : [];
    console.log('Expense Data:', expensesData);
  // Income data: only transactions with Credit values.
  const incomeData = selectedEvaluation?.evaluation_result.transactions
    ? selectedEvaluation.evaluation_result.transactions
        .filter((tx: Transaction) => tx.Credit !== null)
        .map((tx: Transaction, i: number) => ({
          time: tx.Date ? new Date(tx.Date).toLocaleDateString() : `T${i + 1}`,
          income: tx.Credit,
        }))
    : [];

  if (loading) return <div>Loading metrics...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!selectedEvaluation) return <div>No evaluation selected.</div>;

  // Function to handle selecting a different applicant
  const handleSelectEvaluation = (evalId: number) => {
    const evalSelected = evaluations.find((e) => e.id === evalId);
    if (evalSelected) setSelectedEvaluation(evalSelected);
  };

  // For the "All Metrics" table, assume metrics are stored under evaluation_result.metrics.
  const metricsObj: Metrics = selectedEvaluation.evaluation_result.metrics || defaultMetrics;
  const orderedMetrics: { key: keyof Metrics; format: 'currency' | 'float'; displayName: string }[] = [
    { key: 'starting_balance', format: 'currency', displayName: 'Starting Balance' },
    { key: 'ending_balance', format: 'currency', displayName: 'Ending Balance' },
    { key: 'max_balance', format: 'currency', displayName: 'Max Balance' },
    { key: 'min_balance', format: 'currency', displayName: 'Min Balance' },
    { key: 'total_income', format: 'currency', displayName: 'Total Income' },
    { key: 'total_expenses', format: 'currency', displayName: 'Total Expenses' },
    { key: 'net_cash_flow', format: 'currency', displayName: 'Net Cash Flow' },
    { key: 'essential_spending', format: 'currency', displayName: 'Essential Spending' },
    { key: 'discretionary_spending', format: 'currency', displayName: 'Discretionary Spending' },
    { key: 'spending_std', format: 'float', displayName: 'Spending Std Dev' },
    { key: 'spending_cv', format: 'float', displayName: 'Spending CV' },
    { key: 'max_balance_ratio', format: 'float', displayName: 'Max Balance Ratio' },
    { key: 'min_balance_ratio', format: 'float', displayName: 'Min Balance Ratio' },
  ];

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Metrics</h1>
      
      {/* Filter: applicant name selection */}
      <div style={{ marginBottom: '1rem' }}>
        <label>
          Filter by Applicant Name: 
          <input
            type="text"
            value={filterName}
            onChange={(e) => setFilterName(e.target.value)}
            style={{ marginLeft: '0.5rem' }}
          />
        </label>
      </div>
      
      {/* List of evaluations to select */}
      <div style={{ marginBottom: '1rem' }}>
        <h3>Select Applicant:</h3>
        {filteredEvaluations.map((evalRec) => (
          <button 
          key={evalRec.id} 
          onClick={() => handleSelectEvaluation(evalRec.id)}
          style={{
            marginRight: '0.5rem',
            marginBottom: '0.5rem',
            padding: '0.5rem 1rem',
            backgroundColor: selectedEvaluation?.id === evalRec.id ? '#4CAF50' : '#f0f0f0',
            color: selectedEvaluation?.id === evalRec.id ? 'white' : 'black',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          {evalRec.evaluation_result.applicantName}
        </button>
        ))}
      </div>
      
      {/* Display text with applicant name and loan eligibility score */}
      <div style={{ marginBottom: '2rem' }}>
  <h2>
    This is applicant <strong>{selectedEvaluation.evaluation_result.applicantName}</strong> with a loan eligibility score of{' '}
    <strong>{Math.trunc(selectedEvaluation.evaluation_result.loan_eligibility_score)}</strong>
  </h2>
  <p><em>{computeLoanRecommendation(selectedEvaluation.evaluation_result.loan_eligibility_score)}</em></p>
</div>
      
      {/* Chart 1: Balance Over Time */}
      <div style={{ marginBottom: '2rem' }}>
  <h3>Balance Over Time</h3>
  {balanceData.length > 0 ? (
    <LineChart width={600} height={300} data={balanceData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="time" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="balance" stroke="#8884d8" activeDot={{ r: 8 }} />
    </LineChart>
  ) : (
    <div>No balance data available.</div>
  )}
</div>
      
      {/* Chart 2: Expenses Over Time */}
      <div style={{ marginBottom: '2rem' }}>
        <h3>Expenses Over Time</h3>
        <LineChart width={500} height={300} data={expensesData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="expense" stroke="#82ca9d" activeDot={{ r: 8 }} />
        </LineChart>
      </div>
      
      {/* Chart 3: Income Over Time */}
      <div style={{ marginBottom: '2rem' }}>
        <h3>Income Over Time</h3>
        <LineChart width={500} height={300} data={incomeData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="income" stroke="#ff7300" activeDot={{ r: 8 }} />
        </LineChart>
      </div>
      
      {/* Chart 4: Table of All Metrics */}
      <div style={{ marginBottom: '2rem' }}>
  <h3>All Metrics</h3>
  <table style={{ borderCollapse: 'collapse', width: '100%' }}>
    <tbody>
      {orderedMetrics.map(({ key, format, displayName }) => {
        const value = metricsObj[key];
        
        // Skip rendering if the metric does not exist
        if (value === undefined || value === null) return null;

        // Format the value based on its type
        const formattedValue = format === 'currency'
          ? `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
          : Number(value).toFixed(2);

        return (
          <tr key={key}>
            <td style={{ border: '1px solid black', padding: '0.5rem', fontWeight: 'bold' }}>
              {displayName}
            </td>
            <td style={{ border: '1px solid black', padding: '0.5rem' }}>{formattedValue}</td>
          </tr>
        );
      })}
    </tbody>
  </table>
</div>
      
      {/* Chart 5: Table of All Expenses (Transactions) */}
      <div style={{ marginBottom: '2rem' }}>
  <h3>Transactions</h3>
  <table style={{ borderCollapse: 'collapse', width: '100%' }}>
    <thead>
      <tr>
        <th style={{ border: '1px solid black', padding: '0.5rem' }}>Date</th>
        <th style={{ border: '1px solid black', padding: '0.5rem' }}>Transaction Type</th>
        <th style={{ border: '1px solid black', padding: '0.5rem' }}>Debit</th>
        <th style={{ border: '1px solid black', padding: '0.5rem' }}>Credit</th>
        <th style={{ border: '1px solid black', padding: '0.5rem' }}>Balance</th>
      </tr>
    </thead>
    <tbody>
      {selectedEvaluation.evaluation_result.transactions && selectedEvaluation.evaluation_result.transactions.length > 0 ? (
        selectedEvaluation.evaluation_result.transactions.map((tx: Transaction, index: number) => (
          <tr key={index}>
            <td style={{ border: '1px solid black', padding: '0.5rem' }}>
              {tx.Date ? new Date(tx.Date).toLocaleDateString() : `T${index + 1}`}
            </td>
            <td style={{ border: '1px solid black', padding: '0.5rem' }}>{tx.Category}</td>
            <td style={{ border: '1px solid black', padding: '0.5rem' }}>
              {tx.Debit !== null ? `$${tx.Debit.toFixed(2)}` : '-'}
            </td>
            <td style={{ border: '1px solid black', padding: '0.5rem' }}>
              {tx.Credit !== null ? `$${tx.Credit.toFixed(2)}` : '-'}
            </td>
            <td style={{ border: '1px solid black', padding: '0.5rem' }}>{`$${tx.Balance.toFixed(2)}`}</td>
          </tr>
        ))
      ) : (
        <tr>
          <td colSpan={5} style={{ textAlign: 'center', padding: '1rem' }}>
            No transactions available.
          </td>
        </tr>
      )}
    </tbody>
  </table>
</div>
</div>
  );
};

export default MetricsPage;
