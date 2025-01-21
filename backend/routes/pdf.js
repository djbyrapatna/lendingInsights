// backend/routes/pdf.js
const express = require('express');
const router = express.Router();
const processPdf = require('../services/processPdf'); // We'll create this next
const path = require('path');
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
    
    // Call the Python pipeline wrapper function with the file path.
    const result = await processPdf(filePath);
    
    res.json({ filename: uniqueFilename, ...result });
  } catch (error) {
    console.error('Error processing PDF:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
