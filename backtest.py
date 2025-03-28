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
from prompts import VIOLATIONS_PROMPT
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
    """Parse model response to extract violations information."""
    try:
        # Extract content between <extraction> tags
        pattern = r'<extraction>(.*?)</extraction>'
        match = re.search(pattern, response, re.DOTALL)
        
        if not match:
            return "N/A", "N/A", "N/A", "N/A"
            
        content = match.group(1).strip()
        
        # Initialize values
        violations = "N/A"
        liens = "N/A"
        collections = "N/A"
        other_issues = "N/A"
        
        # Extract each field
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('Violations:'):
                violations = line.replace('Violations:', '').strip()
            elif line.startswith('Liens:'):
                liens = line.replace('Liens:', '').strip()
            elif line.startswith('Collections:'):
                collections = line.replace('Collections:', '').strip()
            elif line.startswith('Other similar issues:'):
                other_issues = line.replace('Other similar issues:', '').strip()
                
        return violations, liens, collections, other_issues
            
    except Exception as e:
        return f"Error: {str(e)}", f"Error: {str(e)}", f"Error: {str(e)}", f"Error: {str(e)}"

def call_claude_haiku(client, text):
    """Query Claude Haiku with the given text and prompt."""
    try:
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": f"{VIOLATIONS_PROMPT.format(content=text)}"}
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
                {"role": "user", "content": VIOLATIONS_PROMPT.format(content=text)}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def call_gemini(text):
    """Call Gemini Flash 2 API and get response."""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(VIOLATIONS_PROMPT.format(content=text))
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def process_file(pdf_path):
    """Process a single PDF file with all models."""
    filename = os.path.basename(pdf_path)
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        empty_values = ("Error: Could not extract text", "Error: Could not extract text", 
                       "Error: Could not extract text", "Error: Could not extract text")
        return {
            'file_name': filename,
            'raw_responses': {
                'claude_haiku': 'Error: Could not extract text',
                'gpt4o_mini': 'Error: Could not extract text',
                'gemini_flash': 'Error: Could not extract text'
            },
            'claude_haiku_violations': empty_values[0],
            'claude_haiku_liens': empty_values[1],
            'claude_haiku_collections': empty_values[2],
            'claude_haiku_other': empty_values[3],
            'gpt4o_mini_violations': empty_values[0],
            'gpt4o_mini_liens': empty_values[1],
            'gpt4o_mini_collections': empty_values[2],
            'gpt4o_mini_other': empty_values[3],
            'gemini_violations': empty_values[0],
            'gemini_liens': empty_values[1],
            'gemini_collections': empty_values[2],
            'gemini_other': empty_values[3]
        }
    
    results = {'file_name': filename}
    raw_responses = {}
    
    # Process Claude Haiku model
    haiku_response = call_claude_haiku(anthropic, text)
    raw_responses['claude_haiku'] = haiku_response
    violations, liens, collections, other = parse_model_response(haiku_response)
    results['claude_haiku_violations'] = violations
    results['claude_haiku_liens'] = liens
    results['claude_haiku_collections'] = collections
    results['claude_haiku_other'] = other
    
    # Process GPT-4o-mini model
    gpt4o_mini_response = call_gpt4(text)
    raw_responses['gpt4o_mini'] = gpt4o_mini_response
    violations, liens, collections, other = parse_model_response(gpt4o_mini_response)
    results['gpt4o_mini_violations'] = violations
    results['gpt4o_mini_liens'] = liens
    results['gpt4o_mini_collections'] = collections
    results['gpt4o_mini_other'] = other
    
    # Process Gemini Flash model
    gemini_response = call_gemini(text)
    raw_responses['gemini_flash'] = gemini_response
    violations, liens, collections, other = parse_model_response(gemini_response)
    results['gemini_violations'] = violations
    results['gemini_liens'] = liens
    results['gemini_collections'] = collections
    results['gemini_other'] = other
    
    # Add raw responses to results
    results['raw_responses'] = raw_responses
    
    return results

def main():
    # Get list of PDF files
    pdf_files = [os.path.join('files', f) for f in os.listdir('files') if f.endswith('.pdf')]
    
    results = []
    
    print(f"Processing {len(pdf_files)} files for violations, liens, and collections...")
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
    fields = ['violations', 'liens', 'collections', 'other']
    models = ['claude_haiku', 'gpt4o_mini', 'gemini']
    
    for model in models:
        for field in fields:
            column_order.append(f'{model}_{field}')
    
    df = df[column_order]
    
    # Save results
    csv_filename = 'violations_results.csv'
    json_filename = 'violations_results_with_raw.json'
    
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