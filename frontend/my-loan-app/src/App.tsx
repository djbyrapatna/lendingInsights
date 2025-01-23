//import { useState } from 'react'
//import reactLogo from './assets/react.svg'
//import viteLogo from '/vite.svg'
import './App.css'

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import LandingPage from './pages/LandingPage';
import UploadPage from './pages/UploadPage';
import MetricsPage from './pages/MetricsPage';
import LoanEligibilityPage from './pages/LoanEligibilityPage';

const App: React.FC = () => {
  return (
    <Router>
      <nav>
        {/* Simple navigation links */}
        <Link to="/">Home</Link> | 
        <Link to="/upload">Upload PDF</Link> | 
        <Link to="/metrics">Metrics</Link> | 
        <Link to="/loan">Loan Eligibility</Link>
      </nav>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/metrics" element={<MetricsPage />} />
        <Route path="/loan" element={<LoanEligibilityPage />} />
      </Routes>
    </Router>
  );
};

export default App;
