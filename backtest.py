import os
import pandas as pd
from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai
import PyPDF2
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import json
import re
from prompts import ADDRESS_NAMES_PROMPT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize API clients
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

# Model configurations
CLAUDE_MODELS = [
    "claude-3-5-haiku-20241022"
]

GPT4_MODEL = "gpt-4o-mini-2024-07-18"
GEMINI_MODEL = "gemini-2.0-flash"

# The prompt template
PROMPT_TEMPLATE = """You are tasked with reviewing a PDF document and extracting specific dates. This task is crucial,
and accuracy is of utmost importance. 

Your goal is to precisely extract three dates from the PDF:
1. Good Through Date
2. Closing Date
3. Dues/Assessments paid to/through

Follow these steps to complete the task:

1. Carefully read through the entire PDF content.

2. For each of the three required dates:
a. Look for exact phrases or close variations of "Good Through Date," "Closing Date," and
"Dues/Assessments paid to/through."
b. Here are some close variations for "Good Through Date" - "good through", "valid until", "expires on", "effective through" or similar terminology that
might indicate the date you're searching for.
c. If you find an associated date, extract it exactly as it appears in the document.
d. If a date is not present or unclear, do not guess or infer. Instead, use "N/A" or "Unclear"
respectively.

3. For Good Through Date consider these cases:
a. If the documents states something like "90 calendar days from the order date" look at the order date (or prepare date)" and compute 90 calendar days from it.
 90 calendar days here is just an example to illustrate the point - it could be 30 days or any other number.
b. If the documents states something like "30 days from the date of closing" look at the closing date and compute 30 days from it. 30 days is just an example to illustrate the point - it could be 60 days or any other number.

4. For Closing Date consider these cases:
a. Closing Date can sometimes be Date of Closing
b. Sometimes the Closing Date will be Estimate Closing date - this is good - use that date for Closing Date
c. If there is a field which says Closing Date but it is blank and there is no date then mark it as N/A

5. Be aware that these three dates are highly unlikely to be the same. Do not confuse them with each other, especially the "Good Through Date" and the "Dues/Assessments paid to/through" date. 
If you are confident about the Dues/Assessments paid to/through then it's almost certain this is NOT the Good Through Date. 

6. Pay close attention to the context surrounding each date to ensure you're identifying the correct one. 

7. Double-check your findings to ensure accuracy.

8. If you have any doubts about a date, err on the side of caution and mark it as "Unclear" rather
than providing potentially incorrect information.

9. Present your findings in the following format:

<extracted_dates>
Good Through Date: [Insert date or N/A or Unclear]
Closing Date: [Insert date or N/A or Unclear]
Dues/Assessments paid to/through: [Insert date or N/A or Unclear]
</extracted_dates>

Remember, accuracy is critical. It's better to admit uncertainty than to provide incorrect
information. If you cannot find a date or are unsure about its accuracy, use "N/A" or "Unclear"
accordingly.

Here is the content to analyze:
{content}
"""

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {str(e)}")
        return ""

def parse_model_response(response):
    """Parse model response to extract address and names."""
    try:
        # Extract content between <extraction> tags
        pattern = r'<extraction>(.*?)</extraction>'
        match = re.search(pattern, response, re.DOTALL)
        
        if not match:
            return "N/A", "N/A", "N/A"
            
        content = match.group(1).strip()
        
        # Initialize values
        property_address = "N/A"
        seller_name = "N/A"
        buyer_name = "N/A"
        
        # Extract each field
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('Property Address:'):
                property_address = line.replace('Property Address:', '').strip()
            elif line.startswith('Seller Name:'):
                seller_name = line.replace('Seller Name:', '').strip()
            elif line.startswith('Buyer Name:'):
                buyer_name = line.replace('Buyer Name:', '').strip()
                
        return property_address, seller_name, buyer_name
            
    except Exception as e:
        return f"Error: {str(e)}", f"Error: {str(e)}", f"Error: {str(e)}"

def call_claude_haiku(client, text):
    """Query Claude Haiku with the given text and prompt."""
    try:
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": f"{ADDRESS_NAMES_PROMPT.format(content=text)}"}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error querying Claude Haiku: {e}")
        return f"Error: {str(e)}"

def call_gpt4(text):
    """Call GPT-4o-mini API and get response."""
    try:
        response = openai_client.chat.completions.create(
            model=GPT4_MODEL,
            temperature=0.3,
            max_tokens=500,
            messages=[
                {"role": "user", "content": ADDRESS_NAMES_PROMPT.format(content=text)}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def call_gemini(text):
    """Call Gemini Flash 2 API and get response."""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(ADDRESS_NAMES_PROMPT.format(content=text))
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def process_file(pdf_path):
    """Process a single PDF file with all models."""
    filename = os.path.basename(pdf_path)
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        empty_values = ("Error: Could not extract text", "Error: Could not extract text", "Error: Could not extract text")
        return {
            'file_name': filename,
            'raw_responses': {
                'claude_haiku': 'Error: Could not extract text',
                'gpt4o_mini': 'Error: Could not extract text',
                'gemini_flash': 'Error: Could not extract text'
            },
            'claude_haiku_address': empty_values[0],
            'claude_haiku_seller': empty_values[1],
            'claude_haiku_buyer': empty_values[2],
            'gpt4o_mini_address': empty_values[0],
            'gpt4o_mini_seller': empty_values[1],
            'gpt4o_mini_buyer': empty_values[2],
            'gemini_address': empty_values[0],
            'gemini_seller': empty_values[1],
            'gemini_buyer': empty_values[2]
        }
    
    results = {'file_name': filename}
    raw_responses = {}
    
    # Process Claude Haiku model
    haiku_response = call_claude_haiku(anthropic, text)
    raw_responses['claude_haiku'] = haiku_response
    address, seller, buyer = parse_model_response(haiku_response)
    results['claude_haiku_address'] = address
    results['claude_haiku_seller'] = seller
    results['claude_haiku_buyer'] = buyer
    
    # Process GPT-4o-mini model
    gpt4o_mini_response = call_gpt4(text)
    raw_responses['gpt4o_mini'] = gpt4o_mini_response
    address, seller, buyer = parse_model_response(gpt4o_mini_response)
    results['gpt4o_mini_address'] = address
    results['gpt4o_mini_seller'] = seller
    results['gpt4o_mini_buyer'] = buyer
    
    # Process Gemini Flash model
    gemini_response = call_gemini(text)
    raw_responses['gemini_flash'] = gemini_response
    address, seller, buyer = parse_model_response(gemini_response)
    results['gemini_address'] = address
    results['gemini_seller'] = seller
    results['gemini_buyer'] = buyer
    
    # Add raw responses to results
    results['raw_responses'] = raw_responses
    
    return results

def main():
    # Get list of PDF files
    pdf_files = [os.path.join('files', f) for f in os.listdir('files') if f.endswith('.pdf')]
    
    results = []
    
    print(f"Processing {len(pdf_files)} files for address and name extraction...")
    for pdf_file in tqdm(pdf_files, desc="Processing files"):
        result = process_file(pdf_file)
        results.append(result)
    
    # Convert results to DataFrame for CSV (excluding raw responses)
    df_results = []
    for result in results:
        df_result = result.copy()
        df_result.pop('raw_responses')  # Remove raw responses for CSV
        df_results.append(df_result)
    
    df = pd.DataFrame(df_results)
    
    # Define column order
    column_order = ['file_name']
    fields = ['address', 'seller', 'buyer']
    models = ['claude_haiku', 'gpt4o_mini', 'gemini']
    
    for model in models:
        for field in fields:
            column_order.append(f'{model}_{field}')
    
    df = df[column_order]
    
    # Save results
    csv_filename = 'address_names_results.csv'
    json_filename = 'address_names_results_with_raw.json'
    
    # Save parsed results to CSV
    df.to_csv(csv_filename, index=False)
    
    # Save complete results including raw responses to JSON
    with open(json_filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nProcessed {len(results)} files. Results saved to:")
    print(f"- {csv_filename} (parsed results)")
    print(f"- {json_filename} (complete results with raw responses)")
    print("\nResults summary:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 30)  # Truncate long filenames
    
    # Create a more readable display format
    display_df = df.copy()
    display_df['file_name'] = display_df['file_name'].apply(lambda x: x.split('_')[0] + '...' + x[-20:])
    
    print(display_df)

if __name__ == "__main__":
    main() 