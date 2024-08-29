import requests
import json
import csv

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
}
api_url = 'https://uk.misumi-ec.com/api_cms/en/navigation.json?_=1724923683592'

def fetch_navigation_data():
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        print("Navigation API Response:")
        print(json.dumps(data, indent=4))
        return data
    except Exception as err:
        print(f"Other error occurred: {err}")
        return None

def extract_product_codes(data):
    prod_code = []
    main_prod = data['navigation'][0]
    First_Cate = main_prod["items"]
    for item in First_Cate:
        if "items" in item:
            for sub_item in item["items"]:
                if "items" in sub_item:
                    for sub_sub_item in sub_item["items"]:
                        print(item['label'], sub_item['label'], sub_sub_item['label'], sub_sub_item['href'])
                        code = sub_sub_item['href'].strip('/').split('/')[-1]
                        prod_code.append(code)
    return prod_code

def read_category_codes(csv_file):
    category_codes = []
    try:
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'category_code' in row:
                    category_codes.append(row['category_code'])
    except FileNotFoundError:
        print(f"The file {csv_file} does not exist.")
    return category_codes

def fetch_data_from_api(category_code):
    api_url = f'https://api.uk.misumi-ec.com/api/v1/series/search?lang=ENG&applicationId=3613ed15-0f92-4dc2-8ebc-5fb1e2e21816&field=%40search&categoryCode={category_code}&page=1&pageSize=100'
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch data for category code {category_code}: {e}")
        return None

def process_series_data(prod_code):
    all_data = []
    for category_code in prod_code[:]:  # Limiting to the first 5 category codes
        data = fetch_data_from_api(category_code)
        if data:
            for item in data.get('seriesList', []):
                product_data = {
                    'department_code': item.get('departmentCode', 'N/A'),
                    'category_code': item.get('categoryCode', 'N/A'),
                    'category_name': item.get('categoryName', 'N/A'),
                    'search_category_code': item.get('searchCategoryCode', 'N/A'),
                    'series_code': item.get('seriesCode', 'N/A'),
                    'series_name': item.get('seriesName', 'N/A'),
                    'brand_code': item.get('brandCode', 'N/A'),
                    'brand_url_code': item.get('brandUrlCode', 'N/A'),
                    'brand_name': item.get('brandName', 'N/A'),
                    'min_standard_days_to_ship': item.get('minStandardDaysToShip', 0),
                    'max_standard_days_to_ship': item.get('maxStandardDaysToShip', 0),
                    'direct_cart_type': item.get('directCartType', 'N/A'),
                    'price_check_less_flag': item.get('priceCheckLessFlag', 'N/A'),
                    'min_standard_unit_price': item.get('minStandardUnitPrice', 0.0),
                    'max_standard_unit_price': item.get('maxStandardUnitPrice', 0.0),
                    'min_price_per_piece': item.get('minPricePerPiece', 0.0),
                    'max_price_per_piece': item.get('maxPricePerPiece', 0.0)
                }
                all_data.append(product_data)
    return all_data

def write_to_csv(data, output_file):
    if not data:
        print("No data to write.")
        return
    keys = data[0].keys()
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as output_csv:
            dict_writer = csv.DictWriter(output_csv, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        print(f"Data successfully written to {output_file}")
    except IOError as e:
        print(f"Failed to write data to CSV: {e}")

if __name__ == "__main__":
    # Fetch and process navigation data
    nav_data = fetch_navigation_data()
    if nav_data:
        # Extract product codes from the navigation data
        prod_code = extract_product_codes(nav_data)
        
        # Write the navigation data to a CSV file
        write_to_csv(nav_data['navigation'], 'navigation_data.csv')
        
        # Fetch, process and write series data to a CSV file
        series_data = process_series_data(prod_code)
        write_to_csv(series_data, 'series_data.csv')
