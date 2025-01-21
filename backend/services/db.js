// backend/services/db.js
const { Pool } = require('pg');

// Use an environment variable or hardcode your connection string.
// Replace 'user', 'password', 'localhost', and 'loan_evaluator_db' with your actual details.
const pool = new Pool({
    connectionString: process.env.DATABASE_URL || 'postgresql://dhruvajb:password@localhost:5432/loan_evaluator_db'
});

module.exports = pool;
