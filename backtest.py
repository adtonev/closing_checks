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
from prompts import ATTACHMENTS_PROMPT
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

GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.5-pro-exp-03-25"
]

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

def parse_attachments_response(response):
    """Parse response for attachments prompt."""
    try:
        pattern = r'<answer>(.*?)</answer>'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "Error: No answer found"
    except Exception as e:
        return f"Error: {str(e)}"

def call_claude_haiku(client, text):
    """Query Claude Haiku with the given text and prompt."""
    try:
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": f"{ATTACHMENTS_PROMPT.format(content=text)}"}
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
                {"role": "user", "content": ATTACHMENTS_PROMPT.format(content=text)}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def call_gemini(text, model_name):
    """Call Gemini API and get response."""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(ATTACHMENTS_PROMPT.format(content=text))
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def process_file(pdf_path):
    """Process a single PDF file with all models."""
    filename = os.path.basename(pdf_path)
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        return {
            'file_name': filename,
            'raw_responses': {
                'claude_haiku': 'Error: Could not extract text',
                'gpt4o_mini': 'Error: Could not extract text',
                'gemini_flash': 'Error: Could not extract text'
            },
            'claude_haiku_attachments': "Error: Could not extract text",
            'gpt4o_mini_attachments': "Error: Could not extract text",
            'gemini_flash_attachments': "Error: Could not extract text"
        }
    
    results = {'file_name': filename}
    raw_responses = {}
    
    # Process with Claude Haiku
    response = call_claude_haiku(anthropic, text)
    raw_responses['claude_haiku'] = response
    results['claude_haiku_attachments'] = parse_attachments_response(response)
    
    # Process with GPT-4o-mini
    response = call_gpt4(text)
    raw_responses['gpt4o_mini'] = response
    results['gpt4o_mini_attachments'] = parse_attachments_response(response)
    
    # Process with Gemini Flash
    response = call_gemini(text, GEMINI_MODELS[0])
    raw_responses['gemini_flash'] = response
    results['gemini_flash_attachments'] = parse_attachments_response(response)
    
    # Add raw responses to results
    results['raw_responses'] = raw_responses
    
    return results

def main():
    # Get list of PDF files
    pdf_files = [os.path.join('files', f) for f in os.listdir('files') if f.endswith('.pdf')]
    
    results = []
    
    print(f"Processing {len(pdf_files)} files for attachments...")
    for pdf_file in tqdm(pdf_files, desc="Processing files"):
        result = process_file(pdf_file)
        results.append(result)
    
    # Convert results to DataFrame for CSV (excluding raw responses)
    df_results = []
    for result in results:
        df_result = {
            'file_name': result['file_name'],
            'claude_haiku_attachments': result['claude_haiku_attachments'],
            'gpt4o_mini_attachments': result['gpt4o_mini_attachments'],
            'gemini_flash_attachments': result['gemini_flash_attachments']
        }
        df_results.append(df_result)
    
    df = pd.DataFrame(df_results)
    
    # Save results
    csv_filename = 'attachments_results.csv'
    json_filename = 'attachments_results_with_raw.json'
    
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