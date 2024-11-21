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

3. Create a `.env` file in the project root and add your Perplexity API key:
```
PERPLEXITY_API_KEY=your_api_key_here
```

## Input File Format

Create a CSV file named `books.csv` with the following columns:
- `title`: Book title
- `year`: Publication year

Example:
```csv
title,year
"Book Title 1",2020
"Book Title 2",2021
```

## Usage

1. Prepare your input file `books.csv`

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
