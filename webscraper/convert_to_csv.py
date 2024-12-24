import json
import csv
import os

def convert_to_csv(data, output_file='facilities.csv'):
    """
    Convert facility data to CSV format
    
    Args:
        data (dict): Scraped facility data
        output_file (str): Path to output CSV file
    """
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
    with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
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
    convert_json_to_csv()
    print("Conversion completed. Output saved to facilities.csv")
