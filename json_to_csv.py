import json
import csv
import os

def convert_json_to_csv():
    # Read the JSON file
    with open('property_info_results.json', 'r') as f:
        data = json.load(f)
    
    # Define CSV headers
    headers = [
        'file_name',
        'claude_haiku_property_address',
        'claude_haiku_seller_name',
        'claude_haiku_buyer_name',
        'claude_haiku_hoa_name',
        'claude_haiku_pm_name',
        'claude_haiku_additional_associations',
        'claude_haiku_file_number',
        'claude_haiku_document_attachments',
        'gpt4o_mini_property_address',
        'gpt4o_mini_seller_name',
        'gpt4o_mini_buyer_name',
        'gpt4o_mini_hoa_name',
        'gpt4o_mini_pm_name',
        'gpt4o_mini_additional_associations',
        'gpt4o_mini_file_number',
        'gpt4o_mini_document_attachments',
        'gemini_flash_property_address',
        'gemini_flash_seller_name',
        'gemini_flash_buyer_name',
        'gemini_flash_hoa_name',
        'gemini_flash_pm_name',
        'gemini_flash_additional_associations',
        'gemini_flash_file_number',
        'gemini_flash_document_attachments'
    ]
    
    # Write to CSV
    with open('property_info_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for item in data:
            row = {
                'file_name': item['file_name'],
                # Claude Haiku results
                'claude_haiku_property_address': item['claude_haiku']['property_address'],
                'claude_haiku_seller_name': item['claude_haiku']['seller_name'],
                'claude_haiku_buyer_name': item['claude_haiku']['buyer_name'],
                'claude_haiku_hoa_name': item['claude_haiku']['hoa_name'],
                'claude_haiku_pm_name': item['claude_haiku']['pm_name'],
                'claude_haiku_additional_associations': item['claude_haiku']['additional_associations'],
                'claude_haiku_file_number': item['claude_haiku']['file_number'],
                'claude_haiku_document_attachments': item['claude_haiku']['document_attachments'],
                # GPT-4o-mini results
                'gpt4o_mini_property_address': item['gpt4o_mini']['property_address'],
                'gpt4o_mini_seller_name': item['gpt4o_mini']['seller_name'],
                'gpt4o_mini_buyer_name': item['gpt4o_mini']['buyer_name'],
                'gpt4o_mini_hoa_name': item['gpt4o_mini']['hoa_name'],
                'gpt4o_mini_pm_name': item['gpt4o_mini']['pm_name'],
                'gpt4o_mini_additional_associations': item['gpt4o_mini']['additional_associations'],
                'gpt4o_mini_file_number': item['gpt4o_mini']['file_number'],
                'gpt4o_mini_document_attachments': item['gpt4o_mini']['document_attachments'],
                # Gemini Flash results
                'gemini_flash_property_address': item['gemini_flash']['property_address'],
                'gemini_flash_seller_name': item['gemini_flash']['seller_name'],
                'gemini_flash_buyer_name': item['gemini_flash']['buyer_name'],
                'gemini_flash_hoa_name': item['gemini_flash']['hoa_name'],
                'gemini_flash_pm_name': item['gemini_flash']['pm_name'],
                'gemini_flash_additional_associations': item['gemini_flash']['additional_associations'],
                'gemini_flash_file_number': item['gemini_flash']['file_number'],
                'gemini_flash_document_attachments': item['gemini_flash']['document_attachments']
            }
            writer.writerow(row)

if __name__ == "__main__":
    convert_json_to_csv()
    print("CSV file has been created: property_info_results.csv") 