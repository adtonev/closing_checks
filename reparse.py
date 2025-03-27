import json
import re
import pandas as pd

def parse_model_response(response):
    """Parse model response to extract date and confidence."""
    try:
        if "Unable to determine" in response:
            return "Unable to determine", "N/A"
        
        # Look for date in MM/DD/YYYY or MM-DD-YYYY format
        date_pattern = r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})'
        date_match = re.search(date_pattern, response)
        
        # Look for confidence percentage
        confidence_pattern = r'(\d+)%'
        confidence_match = re.search(confidence_pattern, response)
        
        if date_match:
            # Convert to standardized MM/DD/YYYY format
            month, day, year = date_match.groups()
            date = f"{month}/{day}/{year}"
        else:
            date = "Error parsing date"
            
        confidence = confidence_match.group(1) + "%" if confidence_match else "Error parsing confidence"
        
        return date, confidence
    except Exception as e:
        return f"Error: {str(e)}", f"Error: {str(e)}"

# Read the original results
with open('backtest_results.json', 'r') as f:
    results = json.load(f)

# Find the specific file
target_file = "Status_Letter_217-s-25th-ave-brighton-co-80601.pdf"
file_result = next((r for r in results if r["file_name"] == target_file), None)

if file_result:
    print(f"\nResults for {target_file}:")
    for key, value in file_result.items():
        print(f"{key}: {value}")
else:
    print(f"File {target_file} not found in results")

# Convert to DataFrame
df = pd.DataFrame(results)

# Save results to CSV
df.to_csv('backtest_results_reparsed.csv', index=False)

print("\nResults summary:")
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 30)  # Truncate long filenames

# Create a more readable display format
display_df = df.copy()
display_df['file_name'] = display_df['file_name'].apply(lambda x: x.split('_')[0] + '...' + x[-20:])

print(display_df) 