// src/pages/LoanEligibilityPage.tsx
import React from 'react';

const LoanEligibilityPage: React.FC = () => {
  return (
    <div style={{ padding: "2rem" }}>
      <h1>Loan Eligibility</h1>
      <p>This page displays the loan eligibility scores based on the uploaded transactions.</p>
      {/* Future integration: table of candidates and details view */}
      <div>
        <p>[Loan Eligibility Table Placeholder]</p>
      </div>
    </div>
  );
};

export default LoanEligibilityPage;
