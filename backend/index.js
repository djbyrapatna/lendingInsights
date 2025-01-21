// backend/index.js
const express = require('express');
const cors = require('cors');
const pdfRoutes = require('./routes/pdf');  // We'll create this next

const app = express();
const port = process.env.PORT || 8000;

// Use CORS middleware – allow your frontend to access the API.
app.use(cors());
app.use(express.json());

// Mount the PDF processing routes.
app.use('/api/pdf', pdfRoutes);

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
