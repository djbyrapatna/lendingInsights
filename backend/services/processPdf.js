// backend/services/processPdf.js
const { exec } = require('child_process');
const path = require('path');

/**
 * Calls the Python pipeline function to process the PDF.
 * Expects the file path of the PDF and returns a Promise that resolves with the pipeline result.
 */
function processPdf(filePath) {
  return new Promise((resolve, reject) => {
    // Construct the command to run your Python pipeline
    // Adjust the command if your pipeline requires additional arguments.
    const pythonScriptPath = path.join(__dirname, '../../data_processing/pipeline.py');
    const command = `python3 ${pythonScriptPath} "${filePath}"`;
    //const command = `python3 -m data_processing.pipeline.pipeline "${filePath}"`;
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error("Command error:", error);
        return reject(error);
      }
      if (stderr) {
        console.error("Command stderr:", stderr);
        // You may choose to reject or log warnings.
      }
      try {
        // Assuming that your Python pipeline prints JSON output.
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (parseErr) {
        reject(parseErr);
      }
    });
  });
}

module.exports = processPdf;
