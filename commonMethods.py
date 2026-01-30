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
        
    async def enter_text_and_get_response(self, text):
        """
        Enter text in Gemini input field and capture the response
        
        Args:
            text (str): Text to enter in the input field
            
        Returns:
            str: Response from Gemini
        """
        try:
            # Wait for the input field to be available
            await self.page.wait_for_selector('textarea, input[type="text"], [contenteditable="true"]', timeout=10000)
            
            # Find the input field (Gemini uses various selectors)
            input_selectors = [
                'textarea[placeholder*="Enter"]',
                'textarea[placeholder*="prompt"]',
                'textarea[placeholder*="ask"]',
                'textarea',
                'input[type="text"]',
                '[contenteditable="true"]',
                '[data-testid="prompt-textarea"]',
                '.ql-editor'
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    input_element = await self.page.query_selector(selector)
                    if input_element:
                        # Check if it's visible and editable
                        is_visible = await input_element.is_visible()
                        is_enabled = await input_element.is_enabled()
                        if is_visible and is_enabled:
                            break
                except:
                    continue
            
            if not input_element:
                self.logger.error("Could not find input field on the page")
                return "Error: Could not find input field"
            
            # Clear any existing text and enter new text
            await input_element.click()
            await input_element.fill("")  # Clear existing text
            await input_element.type(text, delay=100)  # Type with delay for natural typing
            
            self.logger.info(f"Entered text: {text}")
            
            # Wait a moment for the send button to appear
            await self.page.wait_for_timeout(1000)
            
            # Find and click the send button
            send_selectors = [
                'button[aria-label*="Send"]',
                'button[aria-label*="submit"]',
                'button[type="submit"]',
                'button[data-testid="send-button"]',
                '.send-button',
                'button:has(svg)',
                'button:last-child'
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    send_button = await self.page.query_selector(selector)
                    if send_button:
                        is_visible = await send_button.is_visible()
                        is_enabled = await send_button.is_enabled()
                        if is_visible and is_enabled:
                            break
                except:
                    continue
            
            if send_button:
                await send_button.click()
                self.logger.info("Clicked send button")
            else:
                # Try pressing Enter as fallback
                await input_element.press("Enter")
                self.logger.info("Pressed Enter to send")
            
            # Wait for response to appear
            await self.page.wait_for_timeout(3000)
            
            # Look for response in various possible locations
            response_selectors = [
                '[data-message-author-role="assistant"]',
                '.response-text',
                '.gemini-response',
                '[data-testid="conversation-turn-1"]',
                '.markdown',
                '.response-content',
                'div[class*="response"]',
                'div[class*="answer"]'
            ]
            
            response_text = ""
            for selector in response_selectors:
                try:
                    response_element = await self.page.query_selector(selector)
                    if response_element:
                        response_text = await response_element.text_content()
                        if response_text and len(response_text.strip()) > 0:
                            break
                except:
                    continue
            
            # If no specific response found, try to get the last message
            if not response_text or len(response_text.strip()) == 0:
                try:
                    # Get all text content and try to extract the last meaningful response
                    all_text = await self.page.text_content('body')
                    lines = all_text.split('\n')
                    # Look for non-empty lines that might be responses
                    for line in reversed(lines):
                        if line.strip() and len(line.strip()) > 10 and line.strip() != text:
                            response_text = line.strip()
                            break
                except:
                    pass
            
            if response_text:
                self.logger.info(f"Captured response: {response_text[:100]}...")
                return response_text.strip()
            else:
                self.logger.warning("Could not capture response")
                return "No response captured"
                
        except Exception as e:
            self.logger.error(f"Error entering text and getting response: {e}")
            return f"Error: {str(e)}"
        
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