// backend/services/db.js
const { Pool } = require('pg');
require('dotenv').config(); // Load environment variables from .env

const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    user: process.env.DB_USER || 'dhruvajb',
    password: process.env.DB_PASSWORD || 'password',
    database: process.env.DB_NAME || 'loan_evaluator_db',
});

module.exports = pool;
