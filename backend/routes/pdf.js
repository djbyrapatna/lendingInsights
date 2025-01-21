// backend/routes/pdf.js
const express = require('express');
const router = express.Router();
const processPdf = require('../services/processPdf'); // We'll create this next
const path = require('path');
const pool = require('../services/db'); // The PostgreSQL pool.
// Use multer for handling file uploads
const multer = require('multer');
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'pdfData/');
  },
  filename: (req, file, cb) => {
    // Extract the file extension, default to '.pdf' if not found.
    const ext = path.extname(file.originalname) || '.pdf';
    // Create a unique filename using the field name and current timestamp.
    cb(null, `${file.fieldname}-${Date.now()}${ext}`);
  }
});

const upload = multer({ storage: storage });

// POST /api/pdf/process
router.post('/process', upload.single('file'), async (req, res) => {
  try {
    // The file is available at req.file from multer.
    const filePath = req.file.path;
    const filename = req.file.filename;
    const applicantName = req.body.applicantName || "Unknown";
    // Call the Python pipeline wrapper function with the file path.
    const result = await processPdf(filePath);

    const finalResult = { 
      applicantName, 
      ...result 
    };

    const insertQuery = `
      INSERT INTO loan_evaluations (filename, evaluation_result)
      VALUES ($1, $2)
      RETURNING id;
    `;
    // Convert the result object to JSON.
    const values = [filename, JSON.stringify(finalResult)];
    const dbResult = await pool.query(insertQuery, values);
    
    // Send back the result, possibly including the new record's ID.
    res.json({ id: dbResult.rows[0].id, filename, ...finalResult });
    
    //res.json({ filename: uniqueFilename, ...result });
  } catch (error) {
    console.error('Error processing PDF:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
