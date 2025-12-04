import pandas as pd
import requests
from typing import Optional, List
import io
from urllib.parse import urlparse

def count_states_from_url(url: str, state_column: str = 'state') -> int:
    """
    Read a CSV file from a URL and return the number of unique states.
    
    Args:
        url (str): URL to the CSV file (Google Drive, Dropbox, GitHub, etc.)
        state_column (str): Name of the column containing state data
    
    Returns:
        int: Number of unique states
    """
    try:
        # Convert Google Drive sharing URL to direct download URL
        if 'drive.google.com' in url:
            url = convert_google_drive_url(url)
        
        # Download the CSV file
        response = requests.get(url)
        response.raise_for_status()
        
        # Read CSV from the response content
        df = pd.read_csv(io.StringIO(response.text))
        
        # Check if the state column exists
        if state_column not in df.columns:
            raise KeyError(f"Column '{state_column}' not found. Available columns: {list(df.columns)}")
        
        # Count unique states
        unique_states = df[state_column].dropna().nunique()
        return unique_states
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error downloading file from URL: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing CSV from URL: {str(e)}")

def get_state_list_from_url(url: str, state_column: str = 'state') -> List[str]:
    """
    Read a CSV file from a URL and return a list of unique states.
    
    Args:
        url (str): URL to the CSV file
        state_column (str): Name of the column containing state data
    
    Returns:
        List[str]: Sorted list of unique states
    """
    try:
        # Convert Google Drive sharing URL to direct download URL
        if 'drive.google.com' in url:
            url = convert_google_drive_url(url)
        
        # Download the CSV file
        response = requests.get(url)
        response.raise_for_status()
        
        # Read CSV from the response content
        df = pd.read_csv(io.StringIO(response.text))
        
        # Check if the state column exists
        if state_column not in df.columns:
            raise KeyError(f"Column '{state_column}' not found. Available columns: {list(df.columns)}")
        
        # Get unique states as a sorted list
        unique_states = df[state_column].dropna().unique().tolist()
        return sorted(unique_states)
        
    except Exception as e:
        raise Exception(f"Error processing CSV from URL: {str(e)}")

def convert_google_drive_url(share_url: str) -> str:
    """
    Convert Google Drive sharing URL to direct download URL.
    
    Args:
        share_url (str): Google Drive sharing URL
    
    Returns:
        str: Direct download URL
    """
    try:
        # Extract file ID from Google Drive URL
        if '/file/d/' in share_url:
            file_id = share_url.split('/file/d/')[1].split('/')[0]
        elif 'id=' in share_url:
            file_id = share_url.split('id=')[1].split('&')[0]
        else:
            return share_url  # Return original if not a recognized format
        
        # Create direct download URL
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    except:
        return share_url  # Return original URL if conversion fails

def process_csv_from_cloud(
    url: str, 
    state_column: str = 'state',
    cloud_service: Optional[str] = None
) -> dict:
    """
    Process CSV from various cloud services and return comprehensive state information.
    
    Args:
        url (str): URL to the CSV file
        state_column (str): Name of the column containing state data
        cloud_service (str): Optional hint about cloud service (google_drive, dropbox, etc.)
    
    Returns:
        dict: Dictionary containing state count, list, and metadata
    """
    try:
        # Handle different cloud services
        processed_url = url
        
        if cloud_service == 'google_drive' or 'drive.google.com' in url:
            processed_url = convert_google_drive_url(url)
        elif cloud_service == 'dropbox' or 'dropbox.com' in url:
            # Convert Dropbox sharing URL to direct download
            if '?dl=0' in url:
                processed_url = url.replace('?dl=0', '?dl=1')
        
        # Download and process the file
        response = requests.get(processed_url)
        response.raise_for_status()
        
        # Read CSV
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
            'url': processed_url,
            'message': f"Successfully processed CSV from cloud. Found {state_count} unique states."
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to process CSV from cloud: {str(e)}"
        }

# Example usage
if __name__ == "__main__":
    # Example URLs (replace with your actual cloud file URLs)
    
    # Google Drive example
    google_drive_url = "https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=sharing"
    
    # Dropbox example  
    dropbox_url = "https://www.dropbox.com/s/YOUR_FILE_ID/data.csv?dl=0"
    
    # GitHub raw file example
    github_url = "https://raw.githubusercontent.com/username/repo/main/data.csv"
    
    # Test with a sample URL (this won't work without a real file)
    print("Example usage:")
    print("result = process_csv_from_cloud('your_cloud_url_here', 'state')")
    print("print(result)")
