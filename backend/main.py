from fastapi import FastAPI, File, UploadFile, HTTPException
import shutil
import os
from pipeline.pipeline import document_to_loan_evaluation_pipeline
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Loan Evaluator API")

# Enable CORS (if your frontend is hosted separately)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a directory to temporarily store uploaded files.
UPLOAD_DIR = "pdfData"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process-pdf")
async def process_pdf(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Call your pipeline function.
        labeled_df, metrics_dict, loan_score, msg = document_to_loan_evaluation_pipeline(file_location)
        
        # Convert your labeled_df to a serializable format, for example using .to_dict()
        transactions = labeled_df.to_dict(orient="records")
        return {
            "loan_score": loan_score,
            "message": msg,
            "metrics": metrics_dict,
            "transactions": transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
