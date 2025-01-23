
CREATE TABLE IF NOT EXISTS loan_evaluations (
  id SERIAL PRIMARY KEY,
  pdf_filename VARCHAR(255) NOT NULL,
  evaluation_result JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
