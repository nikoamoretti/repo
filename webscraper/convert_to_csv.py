import json
import csv
import os

def convert_json_to_csv(input_json, output_csv):
    """
    Convert facility data from JSON to CSV format.
    
    Args:
        input_json (str): Path to input JSON file
        output_csv (str): Path to output CSV file
    """
    # Read JSON file
    with open(input_json, 'r') as json_file:
        data = json.load(json_file)
    
    # Prepare CSV headers
    headers = [
        'Facility Name',
        'Location',
        'Products',
        'Railroads',
        'Hazmat Capable',
        'Verification Status'
    ]
    
    # Extract city and state from facility name
    def extract_location(facility_name):
        parts = facility_name.split('|')
        if len(parts) > 1:
            return parts[1].strip()
        return ''
    
    # Create CSV file
    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        
        # Write facility data
        for facility in data['facilities']:
            name = facility['name'].split('|')[0].strip()
            location = extract_location(facility['name'])
            products = ', '.join(facility['products'])
            railroads = ', '.join(facility['railroads'])
            hazmat = 'Yes' if facility['hazmat_capable'] else 'No'
            verification = 'Verified' if facility['type'] == 'verified' else 'Unverified'
            
            writer.writerow([
                name,
                location,
                products,
                railroads,
                hazmat,
                verification
            ])

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert facility data from JSON to CSV')
    parser.add_argument('--input', type=str, required=True, help='Input JSON file')
    parser.add_argument('--output', type=str, required=True, help='Output CSV file')
    args = parser.parse_args()
    
    convert_json_to_csv(args.input, args.output)
    print(f"Conversion completed. Output saved to {args.output}")
