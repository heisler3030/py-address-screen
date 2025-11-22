# py-address-screen

A Python command-line utility for cryptocurrency address screening using the Chainalysis Address Screening API. This is a Python port of the original [node-address-screen](https://github.com/heisler3030/node-address-screen) project.

## Features

- **Bulk Address Screening**: Screen multiple cryptocurrency addresses from CSV files
- **Chainalysis API Integration**: Uses the official Chainalysis Address Screening API
- **Rate Limiting**: Built-in rate limiting to respect API limits
- **Concurrent Processing**: Async processing for improved performance
- **Risk Assessment**: Get risk ratings, categories, and exposure data
- **Direct & Indirect Exposure**: Option to include indirect exposure analysis
- **CSV Input/Output**: Easy-to-use CSV file processing
- **Error Handling**: Robust error handling with detailed logging

## Installation

### Prerequisites

- Python 3.8 or higher
- Chainalysis API key

### Setup

1. Clone the repository:
```bash
git clone git@github.com:heisler3030/py-address-screen.git
cd py-address-screen
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your API key:
```bash
cp .env.example .env
# Edit .env and add your Chainalysis API key
```

## Configuration

Create a `.env` file in the project root with your configuration:

```env
# Required
CHAINALYSIS_API_KEY=your_api_key_here

# Optional configuration
CHAINALYSIS_BASE_URL=https://api.chainalysis.com
RATE_LIMIT=5
MAX_CONCURRENT_REQUESTS=10
INCLUDE_INDIRECT_EXPOSURE=true
```

## Usage

The application requires an input CSV file containing cryptocurrency addresses:

```bash
python main.py addresses.csv
```

You can optionally specify an output file:

```bash
python main.py addresses.csv results.csv
```

If no output file is specified, the application will create one by adding `_screened` to the input filename:
- `addresses.csv` → `addresses_screened.csv`

### Configuration Options

All configuration is done through the `.env` file or environment variables:

- `RATE_LIMIT`: API requests per second (default: 5)
- `MAX_CONCURRENT_REQUESTS`: Maximum concurrent requests (default: 10)
- `INCLUDE_INDIRECT_EXPOSURE`: Include indirect exposure (default: true)
- `CHAINALYSIS_API_KEY`: Your API key (required)

## Input CSV Format

Your input CSV file should contain at least one column with cryptocurrency addresses:

```csv
address,description
1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2,Bitcoin address example
bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh,Bitcoin Bech32 address
0x742d35Cc6638C0532b4f86be76Cc95b3e3e2B0C2,Ethereum address
```

## Output Format

The output CSV includes the following columns:

- `address`: The cryptocurrency address
- `screenStatus`: Screening status or error code (e.g., "complete", "400 Bad Request")
- `risk`: Risk rating (Low, Medium, High, Severe)
- `riskReason`: Detailed risk explanation
- `category`: Primary risk category
- `name`: Entity name (if identified)
- `{category}_direct`: Direct exposure amount for each risk category
- `{category}_indirect`: Indirect exposure amount for each risk category (if enabled)

For addresses that fail to screen, only the `address` and `screenStatus` fields are populated with the error information.

## Examples

### Example: Basic screening
```bash
python main.py example-input.csv
```

### Example: Custom output file
```bash
python main.py addresses.csv my_results.csv
```

## API Rate Limits

The Chainalysis API has rate limits. The default settings (5 requests/second, 10 concurrent) should work well for most use cases. If you experience rate limiting errors, adjust these values in your `.env` file:

```env
RATE_LIMIT=2
MAX_CONCURRENT_REQUESTS=3
```

## Error Handling

The tool handles various error scenarios:

- **API Errors**: Network issues, authentication errors, rate limiting
- **File Errors**: Missing files, invalid CSV format, permission issues
- **Data Errors**: Invalid addresses, missing columns

All errors are logged and included in the output CSV for review.

## Logging

The tool provides informational logging by default. All configuration is managed through environment variables.

## Project Structure

```
py-address-screen/
├── py_address_screen/
│   ├── __init__.py           # Main application logic
│   ├── api_client.py         # Chainalysis API client
│   ├── config.py             # Configuration management
│   └── csv_processor.py      # CSV file processing
├── .env.example              # Environment configuration template
├── .github/
│   └── copilot-instructions.md
├── example-input.csv         # Sample input file
├── main.py                   # Main entry point
├── requirements.txt          # Python dependencies
└── README.md
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

This project follows Python best practices:

- PEP 8 code style
- Type hints
- Comprehensive error handling
- Async/await for concurrent operations

## Differences from Node.js Version

This Python version maintains compatibility with the original Node.js project while adding some improvements:

- **Async/await**: Uses Python's native async capabilities
- **Better Error Handling**: More detailed error reporting
- **Type Hints**: Full type annotation for better code clarity
- **Pandas Integration**: Leverages pandas for CSV processing
- **Simplified Usage**: Environment-based configuration without CLI options

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the same terms as the original node-address-screen project.

## Support

For issues or questions:

1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Include sample data and error messages when possible

## Changelog

### v1.0.0
- Initial Python port from node-address-screen
- Full feature compatibility with original Node.js version
- Async processing for improved performance
- Enhanced error handling and logging