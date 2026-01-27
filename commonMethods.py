import asyncio
from playwright.async_api import async_playwright

# This class handles all browser-related operations using Playwright
# Operations include:
# - Browser initialization and setup with runtime configuration from test data
# - Automatic headless/non-headless mode detection based on version parameter
# - URL navigation and page loading
# - Page information retrieval (title, current URL)
# - Wait operations for timing control
# - Browser cleanup and resource management
# - Test parameter integration for dynamic browser configuration
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
        
    async def setup_browser(self):
        """
        Setup Playwright browser based on test parameters
        Reads version from test_params to determine headless mode
        """
        # Determine headless mode from test parameters
        version = self.test_params.get('version', 'headless')
        headless = version.lower() == 'headless'
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.page = await self.browser.new_page()
        
        # Set viewport size
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
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
            print(f"Navigating to: {url}")
            await self.page.goto(url, wait_until="domcontentloaded")
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
        """Close the browser and clean up resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.browser = None
        self.page = None
        self.playwright = None
        print("Browser closed successfully")