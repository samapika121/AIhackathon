from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import io
from csv_processor import count_states_from_csv, get_state_list_from_csv
from cloud_csv_processor import count_states_from_url, get_state_list_from_url, process_csv_from_cloud
from google_sheets_processor import count_states_from_google_sheets, get_state_list_from_google_sheets, process_google_sheets, get_google_sheets_info

app = FastAPI(
    title="AI Hackathon API",
    description="Backend API for the AI Hackathon project",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example model
class PredictionInput(BaseModel):
    text: Optional[str] = None
    data: Optional[List[float]] = None

class PredictionOutput(BaseModel):
    prediction: str
    confidence: float

class StateCountResponse(BaseModel):
    state_count: int
    states: List[str]
    message: str

class CloudCSVRequest(BaseModel):
    url: str
    state_column: str = "state"
    cloud_service: Optional[str] = None

class GoogleSheetsRequest(BaseModel):
    sheets_url: str
    state_column: str = "state"
    sheet_name: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Hackathon API!"}

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    """
    Example prediction endpoint
    Replace this with your actual AI model prediction logic
    """
    try:
        # This is a placeholder for your actual prediction logic
        # You would typically load your model and make predictions here
        return {
            "prediction": "Example Prediction",
            "confidence": 0.95
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-csv", response_model=StateCountResponse)
async def upload_csv_and_count_states(
    file: UploadFile = File(...),
    state_column: str = "state"
):
    """
    Upload a CSV file and return the number of unique states
    """
    try:
        # Check if file is CSV
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read the uploaded file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Check if the state column exists
        if state_column not in df.columns:
            available_columns = list(df.columns)
            raise HTTPException(
                status_code=400, 
                detail=f"Column '{state_column}' not found. Available columns: {available_columns}"
            )
        
        # Count unique states
        unique_states = df[state_column].dropna().unique().tolist()
        state_count = len(unique_states)
        
        return {
            "state_count": state_count,
            "states": sorted(unique_states),
            "message": f"Successfully processed CSV. Found {state_count} unique states."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/count-states-from-path")
async def count_states_from_file_path(
    file_path: str,
    state_column: str = "state"
):
    """
    Count states from a CSV file using file path
    """
    try:
        state_count = count_states_from_csv(file_path, state_column)
        state_list = get_state_list_from_csv(file_path, state_column)
        
        return {
            "state_count": state_count,
            "states": state_list,
            "message": f"Successfully processed {file_path}. Found {state_count} unique states."
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-cloud-csv")
async def process_cloud_csv(request: CloudCSVRequest):
    """
    Process a CSV file from cloud storage (Google Drive, Dropbox, GitHub, etc.)
    and return comprehensive state information
    """
    try:
        result = process_csv_from_cloud(
            request.url, 
            request.state_column, 
            request.cloud_service
        )
        
        if not result.get('success', False):
            raise HTTPException(
                status_code=400, 
                detail=result.get('error', 'Unknown error processing cloud CSV')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing cloud CSV: {str(e)}")

@app.post("/count-states-from-url", response_model=StateCountResponse)
async def count_states_from_cloud_url(request: CloudCSVRequest):
    """
    Simple endpoint to count states from a cloud CSV URL
    """
    try:
        state_count = count_states_from_url(request.url, request.state_column)
        state_list = get_state_list_from_url(request.url, request.state_column)
        
        return {
            "state_count": state_count,
            "states": state_list,
            "message": f"Successfully processed cloud CSV. Found {state_count} unique states."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-google-sheets")
async def process_google_sheets_endpoint(request: GoogleSheetsRequest):
    """
    Process a Google Sheets document and return comprehensive state information
    """
    try:
        result = process_google_sheets(
            request.sheets_url, 
            request.state_column, 
            request.sheet_name
        )
        
        if not result.get('success', False):
            raise HTTPException(
                status_code=400, 
                detail=result.get('error', 'Unknown error processing Google Sheets')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Google Sheets: {str(e)}")

@app.post("/count-states-from-sheets", response_model=StateCountResponse)
async def count_states_from_google_sheets_endpoint(request: GoogleSheetsRequest):
    """
    Simple endpoint to count states from a Google Sheets document
    """
    try:
        state_count = count_states_from_google_sheets(request.sheets_url, request.state_column)
        state_list = get_state_list_from_google_sheets(request.sheets_url, request.state_column)
        
        return {
            "state_count": state_count,
            "states": state_list,
            "message": f"Successfully processed Google Sheets. Found {state_count} unique states."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sheets-info")
async def get_sheets_info(request: GoogleSheetsRequest):
    """
    Get basic information about a Google Sheets document
    """
    try:
        result = get_google_sheets_info(request.sheets_url)
        
        if not result.get('success', False):
            raise HTTPException(
                status_code=400, 
                detail=result.get('error', 'Unknown error accessing Google Sheets')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sheets info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
