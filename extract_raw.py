import json
import pandas as pd

# Read the JSON file with raw responses
with open('backtest_results_with_raw.json', 'r') as f:
    results = json.load(f)

# Create a list to store the expanded results
expanded_results = []

for result in results:
    row = {
        'file_name': result['file_name'],
        # Claude Haiku dates
        'claude_haiku_good_through': result.get('claude_haiku_good_through', ''),
        'claude_haiku_closing': result.get('claude_haiku_closing', ''),
        'claude_haiku_dues_through': result.get('claude_haiku_dues_through', ''),
        # GPT-4o-mini dates
        'gpt4o_mini_good_through': result.get('gpt4o_mini_good_through', ''),
        'gpt4o_mini_closing': result.get('gpt4o_mini_closing', ''),
        'gpt4o_mini_dues_through': result.get('gpt4o_mini_dues_through', ''),
        # Gemini Flash dates
        'gemini_good_through': result.get('gemini_good_through', ''),
        'gemini_closing': result.get('gemini_closing', ''),
        'gemini_dues_through': result.get('gemini_dues_through', ''),
        # Raw responses
        'claude_haiku_raw_response': result.get('raw_responses', {}).get('claude_haiku', ''),
        'gpt4o_mini_raw_response': result.get('raw_responses', {}).get('gpt4o_mini', ''),
        'gemini_flash_raw_response': result.get('raw_responses', {}).get('gemini_flash', '')
    }
    expanded_results.append(row)

# Convert to DataFrame
df = pd.DataFrame(expanded_results)

# Define column order
column_order = ['file_name']
date_types = ['good_through', 'closing', 'dues_through']
models = ['claude_haiku', 'gpt4o_mini', 'gemini']

# Add date columns
for model in models:
    for date_type in date_types:
        column_order.append(f'{model}_{date_type}')

# Add raw response columns
for model in ['claude_haiku', 'gpt4o_mini', 'gemini_flash']:
    column_order.append(f'{model}_raw_response')

# Reorder columns
df = df[column_order]

# Save to CSV with all details
df.to_csv('backtest_results_with_raw_responses.csv', index=False)

print("Created backtest_results_with_raw_responses.csv with the following columns:")
print("\n".join(f"- {col}" for col in df.columns))
print(f"\nProcessed {len(df)} files") 