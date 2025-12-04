import pandas as pd
from typing import Optional

def count_states_from_csv(file_path: str, state_column: str = 'state') -> int:
    """
    Read a CSV file and return the number of unique states.
    
    Args:
        file_path (str): Path to the CSV file
        state_column (str): Name of the column containing state data (default: 'state')
    
    Returns:
        int: Number of unique states
    
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        KeyError: If the state column doesn't exist in the CSV
        Exception: For other pandas/CSV reading errors
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Check if the state column exists
        if state_column not in df.columns:
            raise KeyError(f"Column '{state_column}' not found in CSV. Available columns: {list(df.columns)}")
        
        # Count unique states (excluding NaN values)
        unique_states = df[state_column].dropna().nunique()
        
        return unique_states
        
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error processing CSV file: {str(e)}")

def get_state_list_from_csv(file_path: str, state_column: str = 'state') -> list:
    """
    Read a CSV file and return a list of unique states.
    
    Args:
        file_path (str): Path to the CSV file
        state_column (str): Name of the column containing state data (default: 'state')
    
    Returns:
        list: List of unique states
    """
    try:
        df = pd.read_csv(file_path)
        
        if state_column not in df.columns:
            raise KeyError(f"Column '{state_column}' not found in CSV. Available columns: {list(df.columns)}")
        
        # Get unique states as a list (excluding NaN values)
        unique_states = df[state_column].dropna().unique().tolist()
        
        return sorted(unique_states)  # Return sorted list
        
    except Exception as e:
        raise Exception(f"Error processing CSV file: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Example usage - replace with your actual CSV file path
    csv_file = "data.csv"
    
    try:
        state_count = count_states_from_csv(csv_file)
        print(f"Number of unique states: {state_count}")
        
        state_list = get_state_list_from_csv(csv_file)
        print(f"States: {state_list}")
        
    except Exception as e:
        print(f"Error: {e}")
