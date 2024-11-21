# Book Information Fetcher

This script uses the Perplexity API to automatically search for and collect information about books, including page counts, ISBN numbers, and publisher information.

## Features

- Batch processing of books
- Automatic search across multiple sources
- Extracts:
  - Page counts
  - ISBN numbers
  - Publisher information
  - Source URLs
  - Citations
- Saves results to CSV
- Rate limit handling
- Robust error handling

## Prerequisites

- Python 3.8 or higher
- Perplexity API key (get one at https://www.perplexity.ai/api-settings)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/book-info-fetcher.git
cd book-info-fetcher
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Perplexity API key:
     ```
     PERPLEXITY_API_KEY=your-api-key-here
     ```

## Input File Format

Create a CSV file named `books.csv` with the following columns:
- `title`: Book title
- `year`: Publication year

Example file (`example_books.csv` is provided):
```csv
title,year
"1793",2017
"1794",2019
"1795",2021
```

## Usage

1. Prepare your input file `books.csv` (or use the provided example_books.csv):
```bash
cp example_books.csv books.csv
```

2. Run the script:
```bash
python script.py
```

3. Check the results in `books_with_pages.csv`

The output file will contain:
- Title
- Year
- Pages
- Note (including ISBN and publisher info)
- URL
- Citations

## Example Output

The script will create a CSV file with entries like:
```csv
title,year,pages,note,url,citations
"1795",2021,458,"Förlag: Bokförlaget Forum, ISBN: 9789137153728","https://www.bokus.com/bok/9789137153728/1795/","[citation data]"
```

## Project Structure

```
book-info-fetcher/
│
├── script.py            # Main script
├── requirements.txt     # Python dependencies
├── example_books.csv    # Example input file
├── .env.example        # Example environment variables
├── .gitignore          # Git ignore rules
├── LICENSE             # MIT license
└── README.md           # This file
```

## Rate Limiting

The script includes built-in rate limiting to respect Perplexity API's limits:
- 20 requests per minute
- 3-second delay between batches
- Batch size of 3 books per request

## Error Handling

The script includes comprehensive error handling:
- API errors
- JSON parsing errors
- File I/O errors
- Missing data handling

## Customization

You can modify the following parameters in `script.py`:
- `BATCH_SIZE`: Number of books per request (default: 3)
- Sleep time between requests (default: 3 seconds)
- Output file name (default: "books_with_pages.csv")

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Anders Barane

## Acknowledgments

- Uses the Perplexity API for book information retrieval
- Built with Python and modern data processing libraries
