import pandas as pd
import time
from typing import List, Dict, Union
import os
from dotenv import load_dotenv
import csv
from tqdm import tqdm
import json
import re
import requests

# Load environment variables
load_dotenv()
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

def fix_json_values(content: str) -> str:
    """Fix common JSON value issues."""
    # Replace unquoted NA with "N/A"
    content = re.sub(r':\s*NA\s*([,}])', ': "N/A"\\1', content)
    # Replace unquoted null with "N/A"
    content = re.sub(r':\s*null\s*([,}])', ': "N/A"\\1', content)
    return content

def extract_json_from_response(response: str) -> List[Dict]:
    """Extract JSON from response that might contain markdown or other formatting."""
    # Remove markdown formatting
    clean_response = response.replace('```json', '').replace('```', '').strip()
    clean_response = fix_json_values(clean_response)
    
    # Try to find any JSON array in the cleaned response
    json_match = re.search(r'\[\s*\{.*?\}\s*\]', clean_response, re.DOTALL)
    if json_match:
        try:
            json_str = json_match.group()
            # Additional cleanup for common issues
            json_str = json_str.replace('NA', '"N/A"')
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {str(e)}")
            print(f"Attempted to parse: {json_str}")
            return None
    return None

def format_citations(citations: Union[List[Dict], List[str], None]) -> List[Dict]:
    """Format citations into a consistent structure."""
    if not citations:
        return []
    
    formatted_citations = []
    for citation in citations:
        if isinstance(citation, str):
            formatted_citations.append({
                "text": "Reference URL",
                "url": citation
            })
        elif isinstance(citation, dict):
            formatted_citations.append({
                "text": citation.get("text", "No text available"),
                "url": citation.get("url", "N/A")
            })
    return formatted_citations

def call_perplexity_api(messages: List[Dict], batch_number: int) -> Dict:
    """Make a call to the Perplexity API using requests."""
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.1-sonar-large-128k-online",
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 2048,
        "top_p": 0.9,
        "return_citations": True
    }
    
    try:
        print(f"\nSending request for batch {batch_number}...")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API call error: {str(e)}")
        if hasattr(response, 'text'):
            print(f"Response text: {response.text}")
        return None

def process_batch(batch_df: pd.DataFrame, messages: List[Dict], batch_number: int, writer) -> None:
    """Process a single batch of books."""
    response_data = call_perplexity_api(messages, batch_number)
    
    if not response_data:
        print(f"No response data for batch {batch_number}")
        return
    
    response_content = response_data['choices'][0]['message']['content']
    citations = format_citations(response_data.get('citations', []))
    
    print(f"\nResponse content:")
    print(response_content)
    print("\nCitations:")
    print(json.dumps(citations, indent=2))
    
    # Parse the response
    results = extract_json_from_response(response_content)
    
    if results:
        # Write results to output file
        for idx, book in enumerate(results):
            if idx < len(batch_df):
                # Convert numeric string to int if possible
                pages = book['pages']
                if isinstance(pages, str) and pages.isdigit():
                    pages = int(pages)
                
                # Get relevant citations for this book
                book_citations = [
                    cite for cite in citations 
                    if book['title'].lower() in cite['text'].lower()
                ]
                
                writer.writerow([
                    book['title'],
                    batch_df.iloc[idx]['year'],
                    pages,
                    book.get('note', ''),
                    book.get('url', 'N/A'),
                    json.dumps(book_citations) if book_citations else '[]'
                ])
        
        # Print progress
        print(f"\nProcessed {len(results)} books in batch {batch_number}:")
        for book in results:
            print(f"\nTitle: {book['title']}")
            print(f"Pages: {book['pages']}")
            print(f"Note: {book.get('note', '')}")
            print(f"URL: {book.get('url', 'N/A')}")
            
            # Print relevant citations
            book_citations = [
                cite for cite in citations 
                if book['title'].lower() in cite['text'].lower()
            ]
            if book_citations:
                print("\nCitations:")
                for cite in book_citations:
                    print(f"- {cite['text']}")
                    print(f"  URL: {cite['url']}")

def process_books_file(input_file: str, output_file: str, batch_size: int = 3):
    """Process the books CSV file in batches."""
    try:
        # Read the input CSV file
        df = pd.read_csv(input_file, encoding='utf-8')
        total_books = len(df)
        print(f"\nTotal books to process: {total_books}")
        
        # Create output file with headers
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['title', 'year', 'pages', 'note', 'url', 'citations'])
            
            # Process in batches
            for i in tqdm(range(0, total_books, batch_size)):
                batch_df = df.iloc[i:i+batch_size]
                batch_books = [
                    {'title': row['title'], 'year': str(row['year'])} 
                    for _, row in batch_df.iterrows()
                ]
                
                try:
                    # Create messages and process batch
                    messages = create_messages(batch_books)
                    process_batch(batch_df, messages, i//batch_size + 1, writer)
                except Exception as e:
                    print(f"Error processing batch: {str(e)}")
                    continue
                
                # Sleep to respect rate limits
                time.sleep(3)
                
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise

def create_messages(books: List[Dict]) -> List[Dict]:
    """Create messages for the Perplexity API."""
    book_list = "\n".join([f"- {book['title']} ({book['year']})" for book in books])
    
    return [
        {
            "role": "system",
            "content": """Du är en expert på att hitta information om svenska böcker.
            För varje bok, sök grundligt efter information om sidantal och andra detaljer.
            VIKTIGT: Formattera alla värden som korrekta JSON-värden, använd "N/A" för saknade värden."""
        },
        {
            "role": "user",
            "content": f"""Sök efter dessa böcker och rapportera sidantal och källinformation:

{book_list}

För varje bok, ange:
1. Exakt sidantal om det finns
2. ISBN om det hittas
3. Förlag och utgivningsår
4. Källan till informationen

VIKTIGT:
- Använd "N/A" (inom citattecken) för saknade värden
- Alla strängar måste vara inom citattecken
- Numeriska värden ska INTE vara inom citattecken

Formattera svaret som JSON:
[
    {{
        "title": "titel",
        "pages": sidantal_eller_NA,
        "note": "förlag, ISBN, och källinformation",
        "url": "url_till_källan"
    }}
]"""
        }
    ]

def main():
    """Main function to run the script."""
    INPUT_FILE = "books.csv"
    OUTPUT_FILE = "books_with_pages.csv"
    BATCH_SIZE = 3
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found!")
        return
    
    if not PERPLEXITY_API_KEY:
        print("Error: Perplexity API key not found in environment variables!")
        return
        
    print(f"Starting to process {INPUT_FILE}")
    process_books_file(INPUT_FILE, OUTPUT_FILE, BATCH_SIZE)
    print(f"Processing complete! Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
