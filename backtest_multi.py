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
from prompts import (
    ATTACHMENTS_PROMPT,
    EXTRA_ASSOCIATIONS_PROMPT,
    DOC_COSTS_PROMPT,
    HOA_NAMES_PROMPT,
    BUYER_APPROVAL_PROMPT
)
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

def parse_extra_associations_response(response):
    """Parse response for extra associations prompt."""
    try:
        pattern = r'<answer>(.*?)</answer>'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "Error: No answer found"
    except Exception as e:
        return f"Error: {str(e)}"

def parse_doc_costs_response(response):
    """Parse response for document costs prompt."""
    try:
        pattern = r'<answers>\s*1\.\s*([^\n]*)\s*2\.\s*([^\n]*)\s*3\.\s*([^\n]*)\s*4\.\s*([^\n]*)\s*</answers>'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return {
                'doc_cost': match.group(1).strip(),
                'rush_order': match.group(2).strip(),
                'rush_fee': match.group(3).strip(),
                'payment_timing': match.group(4).strip()
            }
        return {
            'doc_cost': "Error: No answer found",
            'rush_order': "Error: No answer found",
            'rush_fee': "Error: No answer found",
            'payment_timing': "Error: No answer found"
        }
    except Exception as e:
        return {
            'doc_cost': f"Error: {str(e)}",
            'rush_order': f"Error: {str(e)}",
            'rush_fee': f"Error: {str(e)}",
            'payment_timing': f"Error: {str(e)}"
        }

def parse_hoa_names_response(response):
    """Parse response for HOA names prompt."""
    try:
        pattern = r'<answer>\s*HOA:\s*([^\n]*)\s*PM:\s*([^\n]*)\s*</answer>'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return {
                'hoa_name': match.group(1).strip(),
                'pm_name': match.group(2).strip()
            }
        return {
            'hoa_name': "Error: No answer found",
            'pm_name': "Error: No answer found"
        }
    except Exception as e:
        return {
            'hoa_name': f"Error: {str(e)}",
            'pm_name': f"Error: {str(e)}"
        }

def parse_buyer_approval_response(response):
    """Parse response for buyer approval prompt."""
    try:
        pattern = r'<answer>(.*?)</answer>'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "Error: No answer found"
    except Exception as e:
        return f"Error: {str(e)}"

def call_claude_haiku(client, text, prompt):
    """Query Claude Haiku with the given text and prompt."""
    try:
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": f"{prompt.format(content=text)}"}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error querying Claude Haiku: {e}")
        return f"Error: {str(e)}"

def call_gpt4(text, prompt):
    """Call GPT-4o-mini API and get response."""
    try:
        response = openai_client.chat.completions.create(
            model=GPT4_MODEL,
            temperature=0.3,
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt.format(content=text)}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def call_gemini(text, model_name, prompt):
    """Call Gemini API and get response."""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt.format(content=text))
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def process_file(pdf_path):
    """Process a single PDF file with all prompts and models."""
    filename = os.path.basename(pdf_path)
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        empty_result = {
            'doc_cost': "Error: Could not extract text",
            'rush_order': "Error: Could not extract text",
            'rush_fee': "Error: Could not extract text",
            'payment_timing': "Error: Could not extract text"
        }
        empty_hoa_result = {
            'hoa_name': "Error: Could not extract text",
            'pm_name': "Error: Could not extract text"
        }
        return {
            'file_name': filename,
            'raw_responses': {},
            'attachments': {
                'claude_haiku': "Error: Could not extract text",
                'gpt4o_mini': "Error: Could not extract text",
                'gemini_flash': "Error: Could not extract text"
            },
            'extra_associations': {
                'claude_haiku': "Error: Could not extract text",
                'gpt4o_mini': "Error: Could not extract text",
                'gemini_flash': "Error: Could not extract text"
            },
            'doc_costs': {
                'claude_haiku': empty_result.copy(),
                'gpt4o_mini': empty_result.copy(),
                'gemini_flash': empty_result.copy()
            },
            'hoa_names': {
                'claude_haiku': empty_hoa_result.copy(),
                'gpt4o_mini': empty_hoa_result.copy(),
                'gemini_flash': empty_hoa_result.copy()
            },
            'buyer_approval': {
                'claude_haiku': "Error: Could not extract text",
                'gpt4o_mini': "Error: Could not extract text",
                'gemini_flash': "Error: Could not extract text"
            }
        }
    
    results = {'file_name': filename}
    raw_responses = {}
    
    # Define prompts and their parsers
    prompts_data = {
        'attachments': (ATTACHMENTS_PROMPT, parse_attachments_response),
        'extra_associations': (EXTRA_ASSOCIATIONS_PROMPT, parse_extra_associations_response),
        'doc_costs': (DOC_COSTS_PROMPT, parse_doc_costs_response),
        'hoa_names': (HOA_NAMES_PROMPT, parse_hoa_names_response),
        'buyer_approval': (BUYER_APPROVAL_PROMPT, parse_buyer_approval_response)
    }
    
    # Process with all models
    for prompt_name, (prompt, parser) in prompts_data.items():
        # Initialize results dictionary for this prompt
        if prompt_name not in results:
            results[prompt_name] = {}
        
        # Claude Haiku
        response = call_claude_haiku(anthropic, text, prompt)
        raw_responses[f'claude_haiku_{prompt_name}'] = response
        results[prompt_name]['claude_haiku'] = parser(response)
        
        # GPT-4o-mini
        response = call_gpt4(text, prompt)
        raw_responses[f'gpt4o_mini_{prompt_name}'] = response
        results[prompt_name]['gpt4o_mini'] = parser(response)
        
        # Gemini Flash
        response = call_gemini(text, GEMINI_MODELS[0], prompt)
        raw_responses[f'gemini_flash_{prompt_name}'] = response
        results[prompt_name]['gemini_flash'] = parser(response)
    
    # Add raw responses to results
    results['raw_responses'] = raw_responses
    
    return results

def main():
    # Get list of PDF files
    pdf_files = [os.path.join('files', f) for f in os.listdir('files') if f.endswith('.pdf')]
    
    results = []
    
    print(f"Processing {len(pdf_files)} files for multiple prompts...")
    for pdf_file in tqdm(pdf_files, desc="Processing files"):
        result = process_file(pdf_file)
        results.append(result)
    
    # Convert results to DataFrame for CSV (excluding raw responses)
    df_results = []
    for result in results:
        df_result = {
            'file_name': result['file_name'],
            # Attachments
            'attachments_claude': result['attachments']['claude_haiku'],
            'attachments_gpt4': result['attachments']['gpt4o_mini'],
            'attachments_gemini': result['attachments']['gemini_flash'],
            # Extra Associations
            'extra_associations_claude': result['extra_associations']['claude_haiku'],
            'extra_associations_gpt4': result['extra_associations']['gpt4o_mini'],
            'extra_associations_gemini': result['extra_associations']['gemini_flash'],
            # Doc Costs
            'doc_cost_claude': result['doc_costs']['claude_haiku']['doc_cost'],
            'doc_cost_gpt4': result['doc_costs']['gpt4o_mini']['doc_cost'],
            'doc_cost_gemini': result['doc_costs']['gemini_flash']['doc_cost'],
            'rush_order_claude': result['doc_costs']['claude_haiku']['rush_order'],
            'rush_order_gpt4': result['doc_costs']['gpt4o_mini']['rush_order'],
            'rush_order_gemini': result['doc_costs']['gemini_flash']['rush_order'],
            'rush_fee_claude': result['doc_costs']['claude_haiku']['rush_fee'],
            'rush_fee_gpt4': result['doc_costs']['gpt4o_mini']['rush_fee'],
            'rush_fee_gemini': result['doc_costs']['gemini_flash']['rush_fee'],
            'payment_timing_claude': result['doc_costs']['claude_haiku']['payment_timing'],
            'payment_timing_gpt4': result['doc_costs']['gpt4o_mini']['payment_timing'],
            'payment_timing_gemini': result['doc_costs']['gemini_flash']['payment_timing'],
            # HOA Names
            'hoa_name_claude': result['hoa_names']['claude_haiku']['hoa_name'],
            'hoa_name_gpt4': result['hoa_names']['gpt4o_mini']['hoa_name'],
            'hoa_name_gemini': result['hoa_names']['gemini_flash']['hoa_name'],
            'pm_name_claude': result['hoa_names']['claude_haiku']['pm_name'],
            'pm_name_gpt4': result['hoa_names']['gpt4o_mini']['pm_name'],
            'pm_name_gemini': result['hoa_names']['gemini_flash']['pm_name'],
            # Buyer Approval
            'buyer_approval_claude': result['buyer_approval']['claude_haiku'],
            'buyer_approval_gpt4': result['buyer_approval']['gpt4o_mini'],
            'buyer_approval_gemini': result['buyer_approval']['gemini_flash']
        }
        df_results.append(df_result)
    
    df = pd.DataFrame(df_results)
    
    # Save results
    csv_filename = 'multi_prompt_results.csv'
    json_filename = 'multi_prompt_results_with_raw.json'
    
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