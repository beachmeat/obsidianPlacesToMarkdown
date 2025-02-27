# Google Maps Data to Markdown Converter

This script extracts data from Google Maps URLs using the Google Places API and converts it into Markdown files. It's designed to process a JSON file containing Google Maps URLs and optional metadata, then generate individual Markdown pages for each location.

## Prerequisites

-   Python 3.x
-   `requests` library (`pip install requests`)
-   `beautifulsoup4` library (`pip install beautifulsoup4`)
-   `pyyaml` library (`pip install pyyaml`)
-   A Google Maps Platform API key with the Places API enabled.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install requests beautifulsoup4 pyyaml
    ```

2.  **Obtain a Google Maps API Key:**
    -      Go to the Google Cloud Console.
    -      Create or select a project.
    -      Enable the Places API.
    -      Create API credentials and obtain an API key.

3.  **Set the API Key as an Environment Variable:**
    -      In your terminal, set the `GOOGLE_MAPS_API_KEY` environment variable:
        ```bash
        export GOOGLE_MAPS_API_KEY="YOUR_ACTUAL_API_KEY"
        ```
        -   For persistent storage on macOS, add the above line to your `~/.zshrc` or `~/.bash_profile` file.

4.  **Prepare the Input JSON File:**
    -      Create a JSON file (e.g., `googleMapsSaved.json`) with the following structure:
        ```json
        [
          {
            "URL": "YOUR_GOOGLE_MAPS_URL_1",
            "Comment": "Optional comment",
            "Note": "Optional note"
          },
          {
            "URL": "YOUR_GOOGLE_MAPS_URL_2",
            "Comment": "Another comment",
            "Note": "Another note"
          }
        ]
        ```
    -   Replace `YOUR_GOOGLE_MAPS_URL_1`, `YOUR_GOOGLE_MAPS_URL_2`, etc., with your actual Google Maps URLs.

5.  **Configure the Output Directory:**
    -   In the `main()` function of the Python script, change the `output_dir` variable to the desired output directory for the Markdown files:
        ```python
        output_dir = "/path/to/your/output/directory"
        ```

## Usage

1.  **Run the Script:**
    ```bash
    python your_script_name.py
    ```
    -   Replace `your_script_name.py` with the actual name of your Python script.

2.  **View the Output:**
    -   The script will generate Markdown files in the specified output directory, named after the place names extracted from the Google Maps URLs.

## Script Functionality

-   **`unshorten_url(url)`:** Unshortens shortened URLs to their final destination.
-   **`get_google_maps_data(url, api_key)`:** Fetches data from a Google Maps URL using the Google Places API. It handles different URL formats and extracts relevant information.
-   **`create_markdown_page(data, entry, output_dir)`:** Creates a Markdown page with the extracted information, including frontmatter for metadata.
-   **`main()`:** Main function to run the script, handling file loading, API calls, and Markdown generation.

## Important Notes

-   Ensure your Google Maps API key has sufficient quota for the Places API.
-   The script handles errors gracefully, printing messages for failed API calls or file operations.
-   The generated Markdown files include frontmatter with location, address, tags, URL, and any comments or notes provided in the input JSON file.
-   If a place id cannot be parsed from the url, the script will attempt a text search of the place name.
-   The output directory will be created if it does not already exist.
-   The json file must be in the same directory as the python script, or the path to the json file must be updated in the main function.
