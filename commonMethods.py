import asyncio
import logging
import os
from datetime import datetime
from playwright.async_api import async_playwright

class BrowserOperations:
    def __init__(self, test_params=None):
        """
        Initialize Browser Operations class
        
        Args:
            test_params (dict): Test parameters including version (headless/non-headless)
        """
        self.playwright = None
        self.browser = None
        self.page = None
        self.test_params = test_params or {}
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(logs_dir, f"browser_agent_{timestamp}.log")
        
        # Setup logger
        self.logger = logging.getLogger('BrowserOperations')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        
    async def setup_browser(self):
        """
        Setup Playwright browser based on test parameters
        """
        # Determine headless mode from test parameters
        version = self.test_params.get('version', 'headless')
        headless = version.lower() == 'headless'
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.page = await self.browser.new_page()
        
        # Set viewport size to normal browser dimensions
        await self.page.set_viewport_size({"width": 1366, "height": 768})
        
        self.logger.info(f"Browser opened successfully - Mode: {version}")
        print(f"Chrome browser initialized successfully with Playwright (headless={headless})")
        print(f"Browser mode: {version}")
        
    async def open_url(self, url):
        """
        Open a URL in the browser
        
        Args:
            url (str): The URL to navigate to
        """
        if not self.page:
            await self.setup_browser()
            
        try:
            await self.page.goto(url, wait_until="domcontentloaded")
            print(f"Navigating to: {url}")
            print(f"Successfully opened: {url}")
            
        except Exception as e:
            print(f"Error opening URL: {e}")
            raise
            
    async def get_page_title(self):
        """
        Get the title of the current page
        
        Returns:
            str: Page title
        """
        if self.page:
            return await self.page.title()
        return None
        
    async def get_current_url(self):
        """
        Get the current URL
        
        Returns:
            str: Current URL
        """
        if self.page:
            return self.page.url
        return None
        
    async def wait(self, milliseconds):
        """
        Wait for specified milliseconds
        
        Args:
            milliseconds (int): Time to wait in milliseconds
        """
        await self.page.wait_for_timeout(milliseconds)
        
    async def close_browser(self):
        """
        Close the browser and clean up resources
        """
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
        self.browser = None
        self.page = None
        self.playwright = None
        
        self.logger.info("Browser closed successfully")
        print("Browser closed successfully")