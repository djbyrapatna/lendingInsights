const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://dhruvajb:password@localhost:5432/loan_evaluator_db'
});

// Simple query to test the connection.
pool.query('SELECT NOW()', (err, res) => {
  if (err) {
    console.error('Connection error:', err.stack);
  } else {
    console.log('Connection successful. Current time:', res.rows[0].now);
  }
  pool.end();
});
