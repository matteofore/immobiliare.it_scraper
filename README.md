# immobiliare.it_scraper

This is a Streamlit web scraping project that allows you to easily scrape data about sale and rent, per square meter, from immobiliare.it, which is the main website in Italy for real estate ads. With this web app, you can extract information about regions, provinces, municipalities and neighborhoods (only for the municipalities that are big enough). Furthermore, for some neighborhoods (mostly in big city) the scraper will also extract a list of addresses that are within that area.

## How it works

The scraper allows two input mode: one that support the input from the user through a multiselection (for the regions and provinces) and optionally an user text input for the municipality, while the second way is to load an excel file with the same info as the first input mode (an example file to upload is available in the app).

The logic behind is pretty simple:
- first, a region should be specified, otherwise the entire italian territory will be scraped.
- then, provinces that are within the previously specified regions can be selected, like before, if no province is specified, the entire regions are scraped
- at the end, you can also optionally specify the municipality, but they should be inside the provinces and regions of before, otherwise they will be ignored.

After this in the Analytics page, two simple graphs regarding the data scraped will be displayed.

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https_link
   ```

2. Navigate to the project directory

    ```bash
    cd immobiliare.it_scraper
    ```

3. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    ```

4. Activate the virtual environment:
    - On windows:

        ```bash
        venv\Scripts\activate
        ```

    - On OS/Linux:

        ```bash
        source venv/bin/activate
        ```

5. Install the project dependencies:

    ```bash
    pip install -r requirements.txt
    ```

6. Start the Streamlit app by running the following command:

    ```bash
   streamlit run Home.py
    ```   
