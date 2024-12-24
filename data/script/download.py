import os

import requests
from bs4 import BeautifulSoup


class DataDownloader:
    """
    A class to handle the downloading of files from the OpenSanctions website.
    """

    def __init__(self, base_url, download_dir):
        """
        Initialize the DataDownloader with base URL and download directory.

        :param base_url: Base URL of the website to scrape.
        :param download_dir: Directory to save the downloaded files.
        """
        self.base_url = base_url
        self.download_dir = download_dir

    def fetch_html(self):
        """
        Fetch the HTML content of the base URL.

        :return: Parsed HTML soup object or None if the request fails.
        """
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"Error fetching HTML content: {e}")
            return None

    def find_file_link(self, soup, file_name):
        """
        Find the first matching link containing the specified file name.

        :param soup: Parsed HTML soup object.
        :param file_name: Name of the file to search for in the links.
        :return: Full URL of the file or None if not found.
        """
        links = soup.find_all("a", string=lambda text: text and file_name in text)
        if links:
            href = links[0].get("href")
            if href:
                return (
                    href
                    if href.startswith("http")
                    else os.path.join(self.base_url, href)
                )
        return None

    def download_file(self, file_url, save_path):
        """
        Download a file from a URL and save it to the specified path.

        :param file_url: URL of the file to download.
        :param save_path: Path to save the downloaded file.
        """
        try:
            response = requests.get(file_url)
            response.raise_for_status()  # Raise HTTPError for bad responses
            with open(save_path, "wb") as file:
                file.write(response.content)
            print(f"File saved as: {save_path}")
        except requests.RequestException as e:
            print(f"Error downloading file: {e}")

    def download_data(self, file_name):
        """
        Orchestrates the process of finding and downloading a specific file.

        :param file_name: Name of the file to search for and download.
        """
        soup = self.fetch_html()
        if not soup:
            return

        file_url = self.find_file_link(soup, file_name)
        if not file_url:
            print(f"No links found containing '{file_name}'.")
            return

        print(f"Downloading {file_name}")
        save_path = os.path.join(self.download_dir, file_name)
        self.download_file(file_url, save_path)


# BASE_URL = "https://www.opensanctions.org/datasets/sanctions/"
# DOWNLOAD_DIR = "data/raw-data/"

# # Ensure the download directory exists
# os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# # Create a DataDownloader instance and download the file
# downloader = DataDownloader(BASE_URL, DOWNLOAD_DIR)
# downloader.download_data("entities.ftm.json")
# downloader.download_data("names.txt")
# downloader.download_data("senzing.json")
# downloader.download_data("targets.nested.json")
# downloader.download_data("targets.simple.csv")
