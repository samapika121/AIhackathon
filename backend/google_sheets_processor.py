import pandas as pd
import requests
from typing import Optional, List
import io
from urllib.parse import urlparse
import re

def convert_google_sheets_url(sheets_url: str) -> str:
    """
    Convert Google Sheets sharing URL to CSV export URL.
    
    Args:
        sheets_url (str): Google Sheets sharing URL
    
    Returns:
        str: Direct CSV export URL
    """
    try:
        # Extract spreadsheet ID from various Google Sheets URL formats
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
        ]
        
        sheet_id = None
        for pattern in patterns:
            match = re.search(pattern, sheets_url)
            if match:
                sheet_id = match.group(1)
                break
        
        if not sheet_id:
            raise ValueError("Could not extract sheet ID from URL")
        
        # Extract sheet name/gid if present
        gid = "0"  # Default to first sheet
        gid_match = re.search(r'gid=([0-9]+)', sheets_url)
        if gid_match:
            gid = gid_match.group(1)
        
        # Create CSV export URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        return csv_url
        
    except Exception as e:
        raise ValueError(f"Error converting Google Sheets URL: {str(e)}")

def count_states_from_google_sheets(sheets_url: str, state_column: str = 'state') -> int:
    """
    Read a Google Sheets document and return the number of unique states.
    
    Args:
        sheets_url (str): Google Sheets sharing URL
        state_column (str): Name of the column containing state data
    
    Returns:
        int: Number of unique states
    """
    try:
        # Convert to CSV export URL
        csv_url = convert_google_sheets_url(sheets_url)
        
        # Download the CSV data
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Read CSV from the response content
        df = pd.read_csv(io.StringIO(response.text))
        
        # Check if the state column exists
        if state_column not in df.columns:
            raise KeyError(f"Column '{state_column}' not found. Available columns: {list(df.columns)}")
        
        # Count unique states (excluding NaN values)
        unique_states = df[state_column].dropna().nunique()
        return unique_states
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error accessing Google Sheets: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing Google Sheets: {str(e)}")

def get_state_list_from_google_sheets(sheets_url: str, state_column: str = 'state') -> List[str]:
    """
    Read a Google Sheets document and return a list of unique states.
    
    Args:
        sheets_url (str): Google Sheets sharing URL
        state_column (str): Name of the column containing state data
    
    Returns:
        List[str]: Sorted list of unique states
    """
    try:
        # Convert to CSV export URL
        csv_url = convert_google_sheets_url(sheets_url)
        
        # Download the CSV data
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Read CSV from the response content
        df = pd.read_csv(io.StringIO(response.text))
        
        # Check if the state column exists
        if state_column not in df.columns:
            raise KeyError(f"Column '{state_column}' not found. Available columns: {list(df.columns)}")
        
        # Get unique states as a sorted list (excluding NaN values)
        unique_states = df[state_column].dropna().unique().tolist()
        return sorted(unique_states)
        
    except Exception as e:
        raise Exception(f"Error processing Google Sheets: {str(e)}")

def process_google_sheets(
    sheets_url: str, 
    state_column: str = 'state',
    sheet_name: Optional[str] = None
) -> dict:
    """
    Process Google Sheets and return comprehensive state information.
    
    Args:
        sheets_url (str): Google Sheets sharing URL
        state_column (str): Name of the column containing state data
        sheet_name (str): Optional specific sheet name/tab
    
    Returns:
        dict: Dictionary containing state count, list, and metadata
    """
    try:
        # Convert to CSV export URL
        csv_url = convert_google_sheets_url(sheets_url)
        
        # Download and process the data
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Read the data
        df = pd.read_csv(io.StringIO(response.text))
        
        # Validate column exists
        if state_column not in df.columns:
            return {
                'error': f"Column '{state_column}' not found",
                'available_columns': list(df.columns),
                'success': False
            }
        
        # Process states
        unique_states = df[state_column].dropna().unique().tolist()
        state_count = len(unique_states)
        
        return {
            'success': True,
            'state_count': state_count,
            'states': sorted(unique_states),
            'total_rows': len(df),
            'columns': list(df.columns),
            'sheet_url': sheets_url,
            'csv_export_url': csv_url,
            'message': f"Successfully processed Google Sheets. Found {state_count} unique states."
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to process Google Sheets: {str(e)}"
        }

def get_google_sheets_info(sheets_url: str) -> dict:
    """
    Get basic information about a Google Sheets document.
    
    Args:
        sheets_url (str): Google Sheets sharing URL
    
    Returns:
        dict: Basic information about the sheet
    """
    try:
        csv_url = convert_google_sheets_url(sheets_url)
        response = requests.get(csv_url)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.text))
        
        return {
            'success': True,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'sample_data': df.head(3).to_dict('records'),
            'sheet_url': sheets_url,
            'csv_export_url': csv_url
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Example usage
if __name__ == "__main__":
    # Example Google Sheets URLs
    print("Google Sheets URL formats supported:")
    print("1. https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=0")
    print("2. https://docs.google.com/spreadsheets/d/SHEET_ID/edit?usp=sharing")
    print("3. https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=123456")
    print()
    
    # Example usage (replace with your actual Google Sheets URL)
    example_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0"
    
    print("To use with your Google Sheets:")
    print("1. Open your Google Sheets document")
    print("2. Click 'Share' and set to 'Anyone with the link can view'")
    print("3. Copy the sharing URL")
    print("4. Use it with the functions above")
    print()
    print("Example:")
    print(f"result = process_google_sheets('{example_url}', 'state')")
    print("print(result)")
