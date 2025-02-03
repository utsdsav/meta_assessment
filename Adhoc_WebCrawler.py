import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# The base starting url from which the crawler starts.
BASE_URL = 'https://gentoo.osuosl.org/distfiles/'

def fetch_links(url):
    """
    The functions downloads the page and return a list of href attributes(urls) parsed using BeautifulSoup.
    Parameters: url(the url from which to fetch all the links)
    Returns: A list of links(urls) fetched from the parameter "url" that need to be crawled.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]

def should_skip(link, at_base=False):
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

def crawl(url, relative_path=""):
    """
    Recursively crawls the directory at 'url' and return a list of file paths relative to BASE_URL.
    Parameters: url(the current URL to crawl), relative_path(the path relative to BASE_URL).
    Returns: A list of file paths (as strings) found in the url.
    """
    files = []
    at_base = (relative_path == "")
    links = fetch_links(url)
    
    for link in links:
        if should_skip(link, at_base):
            continue

        # Build the new relative path
        if not link.startswith("http"):
            new_relative = os.path.join(relative_path, link) if relative_path else link
        else:
            if not link.startswith(BASE_URL):
                continue
            new_relative = link[len(BASE_URL):]
        
        new_url = urljoin(url, link)
        
        if link.endswith('/'):
            time.sleep(1) # politeness
            files.extend(crawl(new_url, new_relative))
        else:
            files.append(new_relative)
    return files

if __name__ == '__main__':
    # Crawl the BASE_URL and display the num items found.
    print(f"Starting crawl at {BASE_URL}\n")
    file_list = crawl(BASE_URL)
    print(f"\nFound {len(file_list)} files.")
    
    # Print to console the list of filenames.
    for filename in file_list:
        print(filename)

    # Or you can write the file list to a text file, one filename per line.
    # print("Writing all the filenames to files.txt in the current working directory...\n")
    # with open('files.txt', 'w', encoding='utf-8') as f:
    #     for filename in file_list:
    #         f.write(filename + "\n")
    
    # Crawling finished.
    print("\nFinished crawling the url.")
