// backend/index.js
const express = require('express');
const cors = require('cors');
const pdfRoutes = require('./routes/pdf');  
const path = require('path'); 
const app = express();
const port = process.env.PORT || 8000;

// Use CORS middleware – allow your frontend to access the API.
app.use(cors());
app.use(express.json());

// New Route: Download PDF
app.get('/api/pdf/download/:filename', (req, res) => {
  const { filename } = req.params;

  // Security Check: Prevent directory traversal attacks
  if (filename.includes('..') || path.isAbsolute(filename)) {
    return res.status(400).json({ message: 'Invalid filename.' });
  }

  const filePath = path.join(__dirname, 'pdfData', filename);

  // Check if the file exists
  res.sendFile(filePath, (err) => {
    if (err) {
      console.error(`Error sending file: ${err}`);
      res.status(404).json({ message: 'File not found.' });
    }
  });
});


// Mount the PDF processing routes.
app.use('/api/pdf', pdfRoutes);

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
