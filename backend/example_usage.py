#!/usr/bin/env python3
"""
Example usage of CSV state counting functionality
"""

import pandas as pd
from csv_processor import count_states_from_csv, get_state_list_from_csv
from cloud_csv_processor import count_states_from_url, get_state_list_from_url, process_csv_from_cloud
from google_sheets_processor import count_states_from_google_sheets, get_state_list_from_google_sheets, process_google_sheets, get_google_sheets_info

def create_sample_csv():
    """Create a sample CSV file for testing"""
    data = {
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank'],
        'state': ['California', 'Texas', 'California', 'New York', 'Texas', 'Florida'],
        'age': [25, 30, 35, 28, 32, 27],
        'city': ['Los Angeles', 'Houston', 'San Francisco', 'New York', 'Dallas', 'Miami']
    }
    
    df = pd.DataFrame(data)
    df.to_csv('sample_data.csv', index=False)
    print("Created sample_data.csv with the following data:")
    print(df)
    print()

def main():
    """Main function to demonstrate CSV processing"""
    
    # Create sample data
    create_sample_csv()
    
    # Example 1: Count states from CSV file
    try:
        csv_file = 'sample_data.csv'
        state_count = count_states_from_csv(csv_file, 'state')
        print(f"Number of unique states: {state_count}")
        
        # Get the list of states
        states = get_state_list_from_csv(csv_file, 'state')
        print(f"States found: {states}")
        print()
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Handle different column names
    try:
        # Create another sample with different column name
        data2 = {
            'person': ['John', 'Jane', 'Mike'],
            'location': ['Nevada', 'Oregon', 'Nevada'],
            'score': [85, 92, 78]
        }
        df2 = pd.DataFrame(data2)
        df2.to_csv('sample_data2.csv', index=False)
        
        # Count using different column name
        state_count2 = count_states_from_csv('sample_data2.csv', 'location')
        states2 = get_state_list_from_csv('sample_data2.csv', 'location')
        
        print(f"Sample 2 - Number of unique locations: {state_count2}")
        print(f"Locations found: {states2}")
        
    except Exception as e:
        print(f"Error with sample 2: {e}")
    
    # Example 3: Process CSV from cloud URL
    print("\n" + "="*50)
    print("CLOUD CSV PROCESSING EXAMPLES")
    print("="*50)
    
    # Example cloud URLs (replace with your actual URLs)
    example_urls = {
        "Google Drive": "https://docs.google.com/spreadsheets/d/1cQTrXsGmQ68_EU7gd1OxCQrAX32F-TlXpUqg1xZwUxo/edit?gid=0#gid=0",
        "Dropbox": "https://www.dropbox.com/s/YOUR_FILE_ID/data.csv?dl=0",
        "GitHub Raw": "https://raw.githubusercontent.com/username/repo/main/data.csv",
        "Direct URL": "https://example.com/data.csv"
    }
    
    print("Example cloud URLs you can use:")
    for service, url in example_urls.items():
        print(f"  {service}: {url}")
    
    print("\nTo use with your actual cloud file:")
    print("1. Upload your CSV to Google Drive, Dropbox, or GitHub")
    print("2. Get the sharing URL")
    print("3. Replace the example URL below with your actual URL")
    print("4. Run the script")
    
    # Uncomment and modify this section when you have a real cloud URL
    """
    try:
        # Replace with your actual cloud CSV URL
        cloud_url = "https://drive.google.com/file/d/YOUR_ACTUAL_FILE_ID/view?usp=sharing"
        
        print(f"\nProcessing cloud CSV from: {cloud_url}")
        
        # Method 1: Simple count
        cloud_state_count = count_states_from_url(cloud_url, 'state')
        cloud_states = get_state_list_from_url(cloud_url, 'state')
        
        print(f"Cloud CSV - Number of unique states: {cloud_state_count}")
        print(f"Cloud CSV - States found: {cloud_states}")
        
        # Method 2: Comprehensive processing
        result = process_csv_from_cloud(cloud_url, 'state', 'google_drive')
        
        if result['success']:
            print(f"\nDetailed Results:")
            print(f"  State count: {result['state_count']}")
            print(f"  States: {result['states']}")
            print(f"  Total rows: {result['total_rows']}")
            print(f"  Columns: {result['columns']}")
        else:
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"Error processing cloud CSV: {e}")
    """
    
    # Example 4: Process Google Sheets
    print("\n" + "="*60)
    print("GOOGLE SHEETS PROCESSING EXAMPLES")
    print("="*60)
    
    print("Google Sheets URL formats supported:")
    print("1. https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=0")
    print("2. https://docs.google.com/spreadsheets/d/SHEET_ID/edit?usp=sharing")
    print("3. https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=123456")
    print()
    
    print("To use with your Google Sheets:")
    print("1. Open your Google Sheets document")
    print("2. Click 'Share' and set to 'Anyone with the link can view'")
    print("3. Copy the sharing URL")
    print("4. Use it with the functions below")
    print()
    
    # Uncomment and modify this section when you have a real Google Sheets URL
    """
    try:
        # Replace with your actual Google Sheets URL
        sheets_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0"
        
        print(f"Processing Google Sheets from: {sheets_url}")
        
        # Method 1: Get basic sheet info first
        sheet_info = get_google_sheets_info(sheets_url)
        if sheet_info['success']:
            print(f"Sheet Info:")
            print(f"  Total rows: {sheet_info['total_rows']}")
            print(f"  Total columns: {sheet_info['total_columns']}")
            print(f"  Columns: {sheet_info['columns']}")
            print()
        
        # Method 2: Simple state count
        sheets_state_count = count_states_from_google_sheets(sheets_url, 'state')
        sheets_states = get_state_list_from_google_sheets(sheets_url, 'state')
        
        print(f"Google Sheets - Number of unique states: {sheets_state_count}")
        print(f"Google Sheets - States found: {sheets_states}")
        
        # Method 3: Comprehensive processing
        result = process_google_sheets(sheets_url, 'state')
        
        if result['success']:
            print(f"\nDetailed Results:")
            print(f"  State count: {result['state_count']}")
            print(f"  States: {result['states']}")
            print(f"  Total rows: {result['total_rows']}")
            print(f"  Columns: {result['columns']}")
            print(f"  CSV Export URL: {result['csv_export_url']}")
        else:
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"Error processing Google Sheets: {e}")
    """
    
    print("\n" + "="*50)
    print("USAGE INSTRUCTIONS")
    print("="*50)
    print("To process your Google Sheets:")
    print("1. Uncomment the Google Sheets processing section above")
    print("2. Replace 'YOUR_SHEET_ID' with your actual sheet ID")
    print("3. Make sure your Google Sheets is shared publicly")
    print("4. Run this script again")

def demo_google_sheets_processing(sheets_url: str, state_column: str = 'state'):
    """
    Demo function to process a Google Sheets document
    Call this function with your actual Google Sheets URL
    """
    try:
        print(f"Processing Google Sheets from: {sheets_url}")
        
        # Get comprehensive results
        result = process_google_sheets(sheets_url, state_column)
        
        if result['success']:
            print(f"✓ Success! Found {result['state_count']} unique states")
            print(f"  States: {result['states']}")
            print(f"  Total rows: {result['total_rows']}")
            print(f"  Available columns: {result['columns']}")
            print(f"  CSV Export URL: {result['csv_export_url']}")
            return result
        else:
            print(f"✗ Error: {result['error']}")
            if 'available_columns' in result:
                print(f"  Available columns: {result['available_columns']}")
            return None
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return None

def demo_cloud_processing(url: str, state_column: str = 'state'):
    """
    Demo function to process a cloud CSV file
    Call this function with your actual cloud URL
    """
    try:
        print(f"Processing CSV from: {url}")
        
        # Get comprehensive results
        result = process_csv_from_cloud(url, state_column)
        
        if result['success']:
            print(f"✓ Success! Found {result['state_count']} unique states")
            print(f"  States: {result['states']}")
            print(f"  Total rows: {result['total_rows']}")
            print(f"  Available columns: {result['columns']}")
            return result
        else:
            print(f"✗ Error: {result['error']}")
            return None
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return None

if __name__ == "__main__":
    main()
    
    # Example of how to use the demo functions
    print(f"\n{'='*60}")
    print("QUICK DEMO FUNCTIONS")
    print(f"{'='*60}")
    print("Google Sheets:")
    print("  result = demo_google_sheets_processing('https://docs.google.com/spreadsheets/d/abc123/edit')")
    print("  if result: print(f'Found {result[\"state_count\"]} states')")
    print()
    print("Cloud CSV:")
    print("  result = demo_cloud_processing('https://drive.google.com/file/d/abc123/view')")
    print("  if result: print(f'Found {result[\"state_count\"]} states')")
