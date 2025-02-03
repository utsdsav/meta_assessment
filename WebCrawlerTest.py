import logging
class WebCrawlerTest:
    """Basic tests for the WebCrawler class."""
    def __init__(self, crawler):
        self.crawler = crawler
    
    def run_tests(self):
        """Run all tests."""
        logging.info("Starting tests...")
        self.test_fetch_links()
        logging.info("All tests completed successfully.")
    
    def test_fetch_links(self):
        """
        Test fetching links from the base URL.
        Checks whether the fetch_links returns a list(of all sub_urls).
        """
        links = self.crawler.fetch_links(self.crawler.BASE_URL)
        assert isinstance(links, list)
        logging.info("test_fetch_links passed.")
    