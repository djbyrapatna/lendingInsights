// backend/routes/pdf.js
const express = require('express');
const router = express.Router();
const processPdf = require('../services/processPdf'); // We'll create this next

// Use multer for handling file uploads
const multer = require('multer');
const upload = multer({ dest: 'pdfData/' }); // Files will be saved in pdfData folder

// POST /api/pdf/process
router.post('/process', upload.single('file'), async (req, res) => {
  try {
    // The file is available at req.file from multer.
    const filePath = req.file.path;
    
    // Call the Python pipeline wrapper function with the file path.
    const result = await processPdf(filePath);
    
    res.json(result);
  } catch (error) {
    console.error('Error processing PDF:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
