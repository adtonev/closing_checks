# PDF Information Extractor

This project uses AI models (Claude, GPT-4, and Gemini) to extract information from PDF documents. It can extract:
- Property addresses
- Seller names
- Buyer names
- Dates (good through, closing, dues)

## Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```
ANTHROPIC_API_KEY="your-anthropic-key"
OPENAI_API_KEY="your-openai-key"
GEMINI_API_KEY="your-gemini-key"
```

4. Place your PDF files in a `files` directory in the root of the project.

## Usage

Run the script with:
```bash
python backtest.py
```

The script will process all PDF files in the `files` directory and generate:
- `address_names_results.csv`: Contains parsed results in CSV format
- `address_names_results_with_raw.json`: Contains complete results including raw model responses

## Project Structure

- `backtest.py`: Main script for processing PDFs
- `prompts.py`: Contains prompts for the AI models
- `requirements.txt`: Python dependencies
- `.env`: API keys (not tracked in git)
- `files/`: Directory containing PDF files to process (not tracked in git)

## Notes

- The script saves raw responses from all models for future analysis
- Results are saved in both CSV and JSON formats
- API keys are stored securely in `.env` file (not committed to git) 