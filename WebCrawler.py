import os
import time
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from WebCrawlerTest import WebCrawlerTest

logging.basicConfig(level=logging.INFO)
logging.info("Logging started.")

class WebCrawler:
    def __init__(self, base_url):
        self.BASE_URL = base_url
        logging.info(f"Initialized crawler with base URL: {self.BASE_URL}")


    def fetch_links(self, url):
        """
        The functions downloads the page and return a list of href attributes(urls) parsed using BeautifulSoup.
        Parameters: url(the url from which to fetch all the links)
        Returns: A list of links(urls) fetched from the parameter "url" that need to be crawled.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        return [a['href'] for a in soup.find_all('a', href=True)]

    def should_skip(self, link, at_base=False):
        """
        The function checks if the link should be skipped, i.e. cases like the link beginning
        with sort query (starting with "?") or the 'distfiles' link that takes back to the main directory.
        
        Parameters: link(the url to be crawled), at_base(boolean that states if url at base or not)
        Returns: Boolean(to skip the url or not)
        """
        skip_set = {"parent directory", "../", "/", "distfiles/", "/distfiles/"}
        if link.strip().lower() in skip_set:
            return True
        
        # Skip sort query links that start with "?" (the sort query).
        if link.startswith("?"):
            return True
        
        # If at the base page, also skip any link that starts with "distfiles"
        if at_base and link.lower().startswith("distfiles"):
            return True
        return False

    def crawl(self, url, relative_path=""):
        """
        Recursively crawls the directory at 'url' and return a list of file paths relative to BASE_URL.
        Parameters: url(the current URL to crawl), relative_path(the path relative to BASE_URL).
        Returns: A list of file paths (as strings) found in the url.
        """
        logging.info(f"Processing: {url}")
        files = []
        at_base = (relative_path == "")
        links = self.fetch_links(url)
        
        for link in links:
            if self.should_skip(link, at_base):
                continue

            # Build the new relative path
            if not link.startswith("http"):
                new_relative = os.path.join(relative_path, link) if relative_path else link
            else:
                if not link.startswith(self.BASE_URL):
                    continue
                new_relative = link[len(self.BASE_URL):]
            
            new_url = urljoin(url, link)
            
            if link.endswith('/'):
                time.sleep(1)  # politeness delay
                files.extend(self.crawl(new_url, new_relative))
            else:
                files.append(new_relative)
        return files

    def run(self):
        """Main method to execute the crawling process."""
        logging.info(f"Starting crawl at {self.BASE_URL}")
        file_list = self.crawl(self.BASE_URL)
        logging.info(f"Found {len(file_list)} files.")
        for filename in file_list:
            print(filename)
        
        # Or you can write to file if prefer that over console.

        # logging.info("Writing all the filenames to files.txt in the current working directory...\n")
        # with open('files.txt', 'w', encoding='utf-8') as f:
        #     for filename in file_list:
        #         f.write(filename + "\n")

        logging.info("Finished crawling.")

if __name__ == '__main__':
    # Crawl the BASE_URL.
    # logs the output to the console, you can uncomment the write
    # to file block in the run function if prefer a text file over console.
    BASE_URL = 'https://gentoo.osuosl.org/distfiles/'
    crawler = WebCrawler(BASE_URL)
    crawler.run()

    # Run tests
    test_suite = WebCrawlerTest(crawler)
    test_suite.run_tests()