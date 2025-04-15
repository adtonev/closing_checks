import os
import json
import re
import csv
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
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model configurations
claude_model = "claude-3-haiku-20240307"
gpt4_model = "gpt-4o-mini"
gemini_model = "gemini-1.5-flash"

# Import the prompt
from prompts import DOCUMENT_COSTS_PROMPT

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

def parse_document_costs_response(response):
    """Parse the response from the model to extract document costs information."""
    try:
        # Extract the content between <extraction> tags
        extraction_match = re.search(r'<extraction>(.*?)</extraction>', response, re.DOTALL)
        if not extraction_match:
            return {"error": "No extraction found in response"}
        
        extraction_text = extraction_match.group(1).strip()
        
        # Parse each field
        result = {}
        
        # Document cost
        doc_cost_match = re.search(r'Document cost: (.*?)(?:\n|$)', extraction_text)
        result["document_cost"] = doc_cost_match.group(1).strip() if doc_cost_match else "N/A"
        
        # Processing fee
        proc_fee_match = re.search(r'Processing fee: (.*?)(?:\n|$)', extraction_text)
        result["processing_fee"] = proc_fee_match.group(1).strip() if proc_fee_match else "N/A"
        
        # Rush order status
        rush_order_match = re.search(r'Rush order: (.*?)(?:\n|$)', extraction_text)
        result["rush_order"] = rush_order_match.group(1).strip() if rush_order_match else "N/A"
        
        # Rush fee
        rush_fee_match = re.search(r'Rush fee: (.*?)(?:\n|$)', extraction_text)
        result["rush_fee"] = rush_fee_match.group(1).strip() if rush_fee_match else "N/A"
        
        # Payment timing
        payment_timing_match = re.search(r'Payment timing: (.*?)(?:\n|$)', extraction_text)
        result["payment_timing"] = payment_timing_match.group(1).strip() if payment_timing_match else "N/A"
        
        return result
    except Exception as e:
        return {"error": f"Error parsing response: {e}"}

def call_claude_haiku(text):
    """Call Claude Haiku model with the document costs prompt."""
    try:
        response = claude_client.messages.create(
            model=claude_model,
            max_tokens=4000,
            temperature=0,
            system="You are a helpful assistant that extracts information from PDF documents.",
            messages=[
                {"role": "user", "content": DOCUMENT_COSTS_PROMPT.format(content=text)}
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error calling Claude Haiku: {e}"

def call_gpt4(text):
    """Call GPT-4o-mini model with the document costs prompt."""
    try:
        response = openai.chat.completions.create(
            model=gpt4_model,
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts information from PDF documents."},
                {"role": "user", "content": DOCUMENT_COSTS_PROMPT.format(content=text)}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling GPT-4o-mini: {e}"

def call_gemini(text):
    """Call Gemini Flash model with the document costs prompt."""
    try:
        model = genai.GenerativeModel(gemini_model)
        response = model.generate_content(DOCUMENT_COSTS_PROMPT.format(content=text))
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
    claude_result = parse_document_costs_response(claude_response)
    gpt4_result = parse_document_costs_response(gpt4_response)
    gemini_result = parse_document_costs_response(gemini_response)
    
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
    # Process only the specific invoice file
    target_file = "08628bc5422025-04-11_Order Confirmation - HVW-A00756.pdf"
    pdf_files = [target_file]
    
    print(f"Processing invoice file: {target_file}")
    
    # Process the file
    results = []
    for file_name in tqdm(pdf_files):
        file_path = os.path.join("invoices", file_name)
        result = process_file(file_path)
        results.append(result)
    
    # Save results to JSON file
    with open("document_costs_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Save results to CSV file
    with open("document_costs_results.csv", "w", newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow([
            "file_name",
            "claude_haiku_document_cost",
            "claude_haiku_processing_fee",
            "claude_haiku_rush_order",
            "claude_haiku_rush_fee",
            "claude_haiku_payment_timing",
            "gpt4o_mini_document_cost",
            "gpt4o_mini_processing_fee",
            "gpt4o_mini_rush_order",
            "gpt4o_mini_rush_fee",
            "gpt4o_mini_payment_timing",
            "gemini_flash_document_cost",
            "gemini_flash_processing_fee",
            "gemini_flash_rush_order",
            "gemini_flash_rush_fee",
            "gemini_flash_payment_timing"
        ])
        
        # Write data rows
        for result in results:
            writer.writerow([
                result["file_name"],
                result["claude_haiku"].get("document_cost", "N/A"),
                result["claude_haiku"].get("processing_fee", "N/A"),
                result["claude_haiku"].get("rush_order", "N/A"),
                result["claude_haiku"].get("rush_fee", "N/A"),
                result["claude_haiku"].get("payment_timing", "N/A"),
                result["gpt4o_mini"].get("document_cost", "N/A"),
                result["gpt4o_mini"].get("processing_fee", "N/A"),
                result["gpt4o_mini"].get("rush_order", "N/A"),
                result["gpt4o_mini"].get("rush_fee", "N/A"),
                result["gpt4o_mini"].get("payment_timing", "N/A"),
                result["gemini_flash"].get("document_cost", "N/A"),
                result["gemini_flash"].get("processing_fee", "N/A"),
                result["gemini_flash"].get("rush_order", "N/A"),
                result["gemini_flash"].get("rush_fee", "N/A"),
                result["gemini_flash"].get("payment_timing", "N/A")
            ])
    
    print(f"Results saved to document_costs_results.json and document_costs_results.csv")

if __name__ == "__main__":
    main() 