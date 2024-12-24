# Web Scraper with Cloudflare Protection Bypass

A robust web scraping tool that can handle protected websites and extract structured data. Built with Scrapy and enhanced with Cloudflare protection bypass capabilities.

## Features

- Bypasses Cloudflare protection
- Extracts structured data from websites
- Outputs in both JSON and CSV formats
- Handles dynamic JavaScript content
- Supports multiple data fields (facility names, products, capabilities, etc.)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd webscraper
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

### Basic Usage

Run the scraper with a target URL:
```bash
python3 test_scraper.py --url "YOUR_URL"
```

This will generate two output files:
- `test_result.json`: Raw JSON data
- `facilities.csv`: Formatted CSV data

### Example Output

CSV Format:
```csv
Facility Name,Location,Products,Railroads,Hazmat Capable,Verification Status
"TRANSFLO - Atlanta, GA","Atlanta, GA","Dry Bulk, Food Grade, Liquids",CSX,Yes,Unverified
```

JSON Format:
```json
{
  "facilities": [
    {
      "name": "TRANSFLO - Atlanta, GA",
      "products": ["Dry Bulk", "Food Grade", "Liquids"],
      "railroads": ["CSX"],
      "hazmat_capable": true,
      "type": "verified"
    }
  ]
}
```

## Data Fields

The scraper extracts the following information:
- Facility Name
- Location (City, State)
- Products Handled
- Railroad Connections
- Hazmat Capabilities
- Verification Status

## Error Handling

The scraper includes robust error handling for:
- Connection timeouts
- Protected pages
- Missing data fields
- Invalid URLs

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use and modify as needed.
