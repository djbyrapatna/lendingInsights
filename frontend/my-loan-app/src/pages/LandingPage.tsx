// src/pages/LandingPage.tsx
import React from 'react';

const LandingPage: React.FC = () => {
  return (
    <div style={{ padding: "2rem" }}>
      <h1>Welcome to the Loan Evaluator</h1>
      <p>This tool processes bank transaction statements to assess loan eligibility.</p>
      <p>Use the navigation above to upload your PDF, view metrics, or check loan eligibility details.</p>
    </div>
  );
};

export default LandingPage;
