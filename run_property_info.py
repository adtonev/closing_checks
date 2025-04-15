import os
import json
import re
from PyPDF2 import PdfReader
import anthropic
import openai
import google.generativeai as genai
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Initialize API clients
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure Gemini with API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model configurations
claude_model = "claude-3-haiku-20240307"
gpt4_model = "gpt-4o-mini"
gemini_model = "gemini-1.5-flash"

# Import the prompt
from prompts import PROPERTY_INFO_PROMPT

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

def parse_property_info_response(response):
    """Parse the response from the model to extract property information."""
    try:
        # Extract the content between <extraction> tags
        extraction_match = re.search(r'<extraction>(.*?)</extraction>', response, re.DOTALL)
        if not extraction_match:
            return {"error": "No extraction found in response"}
        
        extraction_text = extraction_match.group(1).strip()
        
        # Parse each field
        result = {}
        
        # Property Address
        address_match = re.search(r'Property Address: (.*?)(?:\n|$)', extraction_text)
        result["property_address"] = address_match.group(1).strip() if address_match else "N/A"
        
        # Seller Name
        seller_match = re.search(r'Seller Name: (.*?)(?:\n|$)', extraction_text)
        result["seller_name"] = seller_match.group(1).strip() if seller_match else "N/A"
        
        # Buyer Name
        buyer_match = re.search(r'Buyer Name: (.*?)(?:\n|$)', extraction_text)
        result["buyer_name"] = buyer_match.group(1).strip() if buyer_match else "N/A"
        
        # HOA Name
        hoa_match = re.search(r'HOA Name: (.*?)(?:\n|$)', extraction_text)
        result["hoa_name"] = hoa_match.group(1).strip() if hoa_match else "N/A"
        
        # PM Name
        pm_match = re.search(r'PM Name: (.*?)(?:\n|$)', extraction_text)
        result["pm_name"] = pm_match.group(1).strip() if pm_match else "N/A"
        
        # Additional HOAs or special districts
        additional_match = re.search(r'Additional HOAs or special districts: (.*?)(?:\n|$)', extraction_text)
        result["additional_associations"] = additional_match.group(1).strip() if additional_match else "N/A"
        
        # File Number
        file_match = re.search(r'File Number: (.*?)(?:\n|$)', extraction_text)
        result["file_number"] = file_match.group(1).strip() if file_match else "N/A"
        
        # Document Attachments
        attachments_match = re.search(r'Document Attachments: (.*?)(?:\n|$)', extraction_text)
        result["document_attachments"] = attachments_match.group(1).strip() if attachments_match else "N/A"
        
        return result
    except Exception as e:
        return {"error": f"Error parsing response: {e}"}

def call_claude_haiku(text):
    """Call Claude Haiku model with the property info prompt."""
    try:
        response = claude_client.messages.create(
            model=claude_model,
            max_tokens=4000,
            temperature=0,
            system="You are a helpful assistant that extracts information from PDF documents.",
            messages=[
                {"role": "user", "content": PROPERTY_INFO_PROMPT.format(content=text)}
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error calling Claude Haiku: {e}"

def call_gpt4(text):
    """Call GPT-4o-mini model with the property info prompt."""
    try:
        response = openai.chat.completions.create(
            model=gpt4_model,
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts information from PDF documents."},
                {"role": "user", "content": PROPERTY_INFO_PROMPT.format(content=text)}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling GPT-4o-mini: {e}"

def call_gemini(text):
    """Call Gemini Flash model with the property info prompt."""
    try:
        model = genai.GenerativeModel(gemini_model)
        response = model.generate_content(PROPERTY_INFO_PROMPT.format(content=text))
        return response.text
    except Exception as e:
        return f"Error calling Gemini Flash: {e}"

def process_file(file_path):
    """Process a single file with all three models."""
    print(f"\nProcessing file: {os.path.basename(file_path)}")
    
    # Extract text from PDF
    text = extract_text_from_pdf(file_path)
    if not text:
        return {
            "file_name": os.path.basename(file_path),
            "error": "Failed to extract text from PDF"
        }
    
    # Call each model
    claude_response = call_claude_haiku(text)
    gpt4_response = call_gpt4(text)
    gemini_response = call_gemini(text)
    
    # Parse responses
    claude_result = parse_property_info_response(claude_response)
    gpt4_result = parse_property_info_response(gpt4_response)
    gemini_result = parse_property_info_response(gemini_response)
    
    # Combine results
    result = {
        "file_name": os.path.basename(file_path),
        "claude_haiku": claude_result,
        "gpt4o_mini": gpt4_result,
        "gemini_flash": gemini_result,
        "raw_responses": {
            "claude_haiku": claude_response,
            "gpt4o_mini": gpt4_response,
            "gemini_flash": gemini_response
        }
    }
    
    return result

def main():
    # Get list of PDF files
    pdf_files = [f for f in os.listdir("files") if f.endswith(".pdf")]
    pdf_files.sort()  # Sort alphabetically
    
    # Process only the first 5 files
    pdf_files = pdf_files[:5]
    
    print(f"Processing {len(pdf_files)} files with PROPERTY_INFO_PROMPT...")
    
    # Process each file
    results = []
    for file_name in tqdm(pdf_files):
        file_path = os.path.join("files", file_name)
        result = process_file(file_path)
        results.append(result)
    
    # Save results to JSON file
    with open("property_info_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to property_info_results.json")

if __name__ == "__main__":
    main() 