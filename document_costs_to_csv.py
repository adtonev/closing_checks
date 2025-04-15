import json
import csv
import os

def convert_json_to_csv():
    # Read the JSON file
    with open('document_costs_results.json', 'r') as f:
        data = json.load(f)
    
    # Define CSV headers
    headers = [
        'file_name',
        'claude_haiku_document_cost',
        'claude_haiku_processing_fee',
        'claude_haiku_rush_order',
        'claude_haiku_rush_fee',
        'claude_haiku_payment_timing',
        'gpt4o_mini_document_cost',
        'gpt4o_mini_processing_fee',
        'gpt4o_mini_rush_order',
        'gpt4o_mini_rush_fee',
        'gpt4o_mini_payment_timing',
        'gemini_flash_document_cost',
        'gemini_flash_processing_fee',
        'gemini_flash_rush_order',
        'gemini_flash_rush_fee',
        'gemini_flash_payment_timing'
    ]
    
    # Write to CSV
    with open('document_costs_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for item in data:
            row = {
                'file_name': item['file_name'],
                # Claude Haiku results
                'claude_haiku_document_cost': item['claude_haiku'].get('document_cost', 'N/A'),
                'claude_haiku_processing_fee': item['claude_haiku'].get('processing_fee', 'N/A'),
                'claude_haiku_rush_order': item['claude_haiku'].get('rush_order', 'N/A'),
                'claude_haiku_rush_fee': item['claude_haiku'].get('rush_fee', 'N/A'),
                'claude_haiku_payment_timing': item['claude_haiku'].get('payment_timing', 'N/A'),
                # GPT-4o-mini results
                'gpt4o_mini_document_cost': item['gpt4o_mini'].get('document_cost', 'N/A'),
                'gpt4o_mini_processing_fee': item['gpt4o_mini'].get('processing_fee', 'N/A'),
                'gpt4o_mini_rush_order': item['gpt4o_mini'].get('rush_order', 'N/A'),
                'gpt4o_mini_rush_fee': item['gpt4o_mini'].get('rush_fee', 'N/A'),
                'gpt4o_mini_payment_timing': item['gpt4o_mini'].get('payment_timing', 'N/A'),
                # Gemini Flash results
                'gemini_flash_document_cost': item['gemini_flash'].get('document_cost', 'N/A'),
                'gemini_flash_processing_fee': item['gemini_flash'].get('processing_fee', 'N/A'),
                'gemini_flash_rush_order': item['gemini_flash'].get('rush_order', 'N/A'),
                'gemini_flash_rush_fee': item['gemini_flash'].get('rush_fee', 'N/A'),
                'gemini_flash_payment_timing': item['gemini_flash'].get('payment_timing', 'N/A')
            }
            writer.writerow(row)

if __name__ == "__main__":
    convert_json_to_csv()
    print("CSV file has been created: document_costs_results.csv") 