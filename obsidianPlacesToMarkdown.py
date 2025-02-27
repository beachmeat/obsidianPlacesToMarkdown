import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import yaml
import os
import json

def unshorten_url(url):
    """Unshortens a URL (e.g., goo.gl) to its final destination."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        response.raise_for_status()  # Check for HTTP errors
        return response.url
    except requests.exceptions.RequestException as e:
        print(f"Error unshortening URL: {e}")
        return url  # Return the original URL if there's an error

def get_google_maps_data(url, api_key):
    """
    Fetches data from a Google Maps URL using the Places API.
    """
    # Unshorten the URL if it's a shortened maps.app.goo.gl link
    original_url = url
    if "maps.app.goo.gl" in url:
        url = unshorten_url(url)
        
    # Extract place ID and name from the URL using regex
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    place_id = None
    
    # Check for the place ID in the 'data' parameter
    if 'data' in query_params:
        data_param = query_params['data'][0]
        place_id_match = re.search(r'!5s(.*?):', data_param)
        if not place_id_match:
           # try to match the other type of data parameter 
           place_id_match = re.search(r'!1s(.*?):', data_param)
        if place_id_match:
            place_id = place_id_match.group(1)
    # Check for the place ID in the path
    if not place_id and parsed_url.path.startswith('/place/'):
        place_id_match = re.search(r'@(.*?),', parsed_url.path)
        if place_id_match:
            place_id = place_id_match.group(1)
            

    if place_id:
        api_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,website,formatted_phone_number,url,geometry,editorial_summary&key={api_key}"
    else:
        # If we don't have place_id, use textsearch to find it.
        place_name_match = re.search(r'/place/([^/@]+)', parsed_url.path)
        if not place_name_match:
          print(f"Could not get a place name from the url: {url}")
          return None
        place_name = place_name_match.group(1).replace("+", " ")
        api_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={place_name}&fields=name,formatted_address,website,formatted_phone_number,url,geometry,editorial_summary&key={api_key}"
    print(f"API URL: {api_url}")

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        print(response.text)
        if data["status"] != "OK":
             if data["status"] == "ZERO_RESULTS" and place_id:
                print(f"API request failed with status: {data['status']}, trying with a text search")
                return get_google_maps_data(url,api_key)
             else:
                print(f"API request failed with status: {data['status']}")
                return None
        else:
            print("API request successful!")
            if place_id:
                data_result= data['result']  # Return the result if it is a place details
            else:
                data_result = data["results"][0]
            data_result["original_url"] = original_url
            return data_result

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def create_markdown_page(data, entry, output_dir):
    """
    Creates a markdown page with the extracted information.
    """
    if not data:
        print("No data provided to create a markdown page.")
        return

    place_name = data.get("name", "Unknown Place")
    location = data.get("geometry", {}).get("location")
    address = data.get("formatted_address", "")
    about = data.get("editorial_summary", {}).get("overview", "")
    place_url = data.get("url", "")
    original_url= data.get("original_url","")
    comment = entry.get("Comment", "")
    note = entry.get("Note", "")

    # Sanitize the filename
    filename = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in place_name)
    filename = filename.strip()
    filename += ".md"
    
    output_path = Path(output_dir) / filename

    # Prepare frontmatter
    frontmatter = {}
    if location:
        frontmatter["location"] = f"{location['lat']},{location['lng']}"
    if address:
        frontmatter["address"] = address
    frontmatter["tags"] = ["camping"]
    if place_url:
        frontmatter["url"] = place_url
    if original_url:
        frontmatter["original_url"] = original_url
    if comment:
        frontmatter["comment"] = comment
    if note:
        frontmatter["note"] = note

    # Create markdown content
    markdown_content = f"# {place_name}\n"
    markdown_content += "---\n"
    markdown_content += yaml.dump(frontmatter)
    markdown_content += "---\n"
    if about:
        markdown_content += f"{about}\n"

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"Markdown page created at: {output_path}")
    except Exception as e:
        print(f"Error creating markdown page: {e}")

def main():
    """Main function to run the script."""
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY") # you need to set the variable with 'export GOOGLE_MAPS_API_KEY="YOUR_ACTUAL_API_KEY"'
    if not api_key:
        print("Error: GOOGLE_MAPS_API_KEY environment variable not set.")
        return

    output_dir = "/ # replace with folder path"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Load the JSON data from the file
    json_file_path = "googleMapsSaved.json"  # Replace with your file path if it's different
    try:
        with open(json_file_path, "r") as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}")
        return

    # Process each entry in the JSON data
    for entry in json_data:
        url = entry.get("URL")
        if url:
            data = get_google_maps_data(url, api_key)
            if data:
                create_markdown_page(data, entry, output_dir)
        else:
            print(f"Warning: No URL found in entry: {entry}")

if __name__ == "__main__":
    main()
