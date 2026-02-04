import asyncio
import logging
import os
import csv
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
        # Use system Chrome instead of bundled Chromium
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
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
            print(f"Navigating to: {url}")
            await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)  # Reduced timeout
            print(f"Successfully opened: {url}")
            # Wait a bit for page to fully load
            await self.page.wait_for_timeout(2000)
            print("Page loaded, checking for authentication...")
            
            # Check if we need to handle authentication
            try:
                # Look for sign-in elements
                sign_in_button = await self.page.query_selector('button:has-text("Sign in"), a:has-text("Sign in")')
                if sign_in_button:
                    print("Sign in button detected. Please sign in to Gemini manually.")
                    print("The browser will stay open for you to sign in.")
                    print("After signing in, press Enter to continue...")
                    input("Press Enter after you have signed in to Gemini...")
                    print("Continuing with the test...")
            except:
                pass
            
            print("Page appears to be ready for interaction")
            return True
            
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
        Enter text in the input field and get response from the AI
        
        Args:
            text (str): Text to enter in the input field
            
        Returns:
            str: The response from the AI
        """
        if not self.page:
            raise Exception("Browser not initialized")
            
        input_field = None
        send_found = False
            
        try:
            print(f"Looking for input field to enter: '{text}'")
            
            # First, let's see what's actually on the page
            print("Checking page content...")
            page_content = await self.page.content()
            print(f"Page title: {await self.page.title()}")
            
            # Try different selectors for Easemate input field
            input_selectors = [
                'textarea[placeholder*="message"]',
                'textarea[placeholder*="Message"]',
                'textarea[placeholder*="ask"]',
                'textarea[placeholder*="Ask"]',
                'textarea[placeholder*="Type"]',
                'textarea[placeholder*="type"]',
                'input[type="text"]',
                'input[placeholder*="message"]',
                'input[placeholder*="Message"]',
                'textarea',
                '[contenteditable="true"]',
                '.input-field',
                '.chat-input',
                '#message-input',
                'input[placeholder*="Type"]',
                'div[role="textbox"]',
                '[role="textbox"]',
                'div[contenteditable="true"]'
            ]
            
            input_found = False
            
            for selector in input_selectors:
                try:
                    print(f"Trying selector: {selector}")
                    elements = await self.page.query_selector_all(selector)
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    
                    if elements:
                        for i, element in enumerate(elements):
                            try:
                                placeholder = await element.get_attribute('placeholder')
                                visible = await element.is_visible()
                                print(f"  Element {i}: placeholder='{placeholder}', visible={visible}")
                                if visible:
                                    input_field = element
                                    input_found = True
                                    print(f"  Using this element!")
                                    break
                            except:
                                pass
                        
                        if input_found:
                            break
                except Exception as e:
                    print(f"  Error with selector {selector}: {e}")
                    continue
            
            if not input_found:
                # Try a more generic approach
                print("Trying generic approach...")
                all_inputs = await self.page.query_selector_all('input, textarea, [contenteditable="true"], [role="textbox"]')
                print(f"Found {len(all_inputs)} total input-like elements")
                
                for i, element in enumerate(all_inputs):
                    try:
                        visible = await element.is_visible()
                        if visible:
                            print(f"  Visible element {i}: {element}")
                            input_field = element
                            input_found = True
                            break
                    except:
                        pass
            
            if not input_found or not input_field:
                raise Exception("Could not find any visible input field")
            
            print(f"Found input field, entering text...")
            await input_field.click()
            await input_field.fill("")  # Clear any existing text
            await input_field.type(text, delay=100)
            
        except Exception as e:
            print(f"Error in input field handling: {e}")
            raise
        
        try:
            # Wait a moment before sending
            await self.page.wait_for_timeout(1000)
            
            print("Looking for send button...")
            
            # Try different selectors for send button
            send_selectors = [
                'button[type="submit"]',
                'button:has-text("Send")',
                'button:has-text("send")',
                'button:has-text("Submit")',
                'button:has-text("submit")',
                'button[aria-label*="Send"]',
                'button[aria-label*="send"]',
                '.send-button',
                '.send-btn',
                'button svg',
                'button:has(svg)',
                'button[class*="send"]',
                'button[class*="submit"]',
                'button[class*="arrow"]',
                'button[class*="right"]'
            ]
            
            for selector in send_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    
                    for element in elements:
                        try:
                            visible = await element.is_visible()
                            if visible:
                                print(f"Found send button with selector: {selector}")
                                await element.click()
                                send_found = True
                                break
                        except:
                            pass
                    
                    if send_found:
                        break
                except:
                    continue
            
            if not send_found:
                print("Send button not found, trying to press Enter")
                try:
                    # Focus back to input field before pressing Enter
                    await input_field.click()
                    await self.page.wait_for_timeout(500)
                    
                    # Try different Enter key combinations
                    await self.page.keyboard.press("Enter")
                    print("Pressed Enter")
                    
                    # If that doesn't work, try Shift+Enter
                    await self.page.wait_for_timeout(1000)
                    await self.page.keyboard.press("Shift+Enter")
                    print("Pressed Shift+Enter")
                    
                except Exception as e:
                    print(f"Error pressing Enter: {e}")
                    # Try one more method
                    await self.page.keyboard.press("Enter")
            
            print("Message sent")
            
            # Wait for response
            print("Waiting for AI response...")
            await self.page.wait_for_timeout(8000)  # Increased wait time
            
            # Check if page is still active
            if self.page.is_closed():
                raise Exception("Page was closed while waiting for response")
            
            # Try different selectors for response
            response_selectors = [
                '.message-content',
                '.response-content',
                '.ai-response',
                '.chat-response',
                '.message',
                '.response',
                '[data-testid*="response"]',
                '[data-testid*="message"]',
                '.prose',
                '.markdown',
                '.text-message',
                '.chat-message',
                '.conversation-turn',
                '.bot-message',
                '.assistant-message',
                '.ai-message',
                'div[class*="message"]',
                'div[class*="response"]',
                'div[class*="chat"]',
                'p',
                'div[class*="text"]'
            ]
            
            print(f"Trying to capture response...")
            response_text = ""
            
            for selector in response_selectors:
                try:
                    print(f"Trying response selector: {selector}")
                    elements = await self.page.query_selector_all(selector)
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    
                    if elements:
                        # Get the last few elements to find the most recent response
                        for element in elements[-3:]:  # Check last 3 elements
                            try:
                                text = await element.text_content()
                                visible = await element.is_visible()
                                print(f"  Element text: {text[:50] if text else 'None'}..., visible: {visible}")
                                
                                if text and visible and len(text.strip()) > 20:  # Filter for substantial responses
                                    # Make sure it's not our own message
                                    if "HI" not in text or len(text.strip()) > 50:
                                        response_text = text
                                        print(f"Found response with selector: {selector}")
                                        break
                            except:
                                pass
                        
                        if response_text:
                            break
                except Exception as e:
                    print(f"  Error with selector {selector}: {e}")
                    continue
            
            # If still no response, try to get all text content and parse
            if not response_text:
                print("Trying to extract response from page content...")
                try:
                    # Wait a bit more for the response to appear
                    await self.page.wait_for_timeout(3000)
                    
                    # Get all text content
                    page_text = await self.page.evaluate('() => document.body.innerText')
                    print(f"Page text length: {len(page_text)}")
                    
                    # Look for text that appears after "HI"
                    if "HI" in page_text:
                        parts = page_text.split("HI")
                        if len(parts) > 1:
                            # Get text after "HI" and clean it up
                            after_hi = parts[-1].strip()
                            lines = after_hi.split('\n')
                            for line in lines:
                                if line.strip() and len(line.strip()) > 20:
                                    response_text = line.strip()
                                    print(f"Extracted response from page content: {response_text[:100]}...")
                                    break
                except Exception as e:
                    print(f"Error extracting from page content: {e}")
            
            if response_text:
                # Clean up the response text
                cleaned_response = response_text.strip()
                # Remove common UI elements that might be captured
                ui_elements = [
                    "Expand menu", "Use microphone", "New chat", "Edit prompt",
                    "Stop response", "Continue", "Regenerate", "Copy", "Share"
                ]
                for element in ui_elements:
                    cleaned_response = cleaned_response.replace(element, "")

                # Clean up extra whitespace and format
                cleaned_response = ' '.join(cleaned_response.split())

                self.logger.info(f"Captured response: {cleaned_response[:100]}...")
                return cleaned_response
            else:
                self.logger.warning("Could not capture response")
                return "No response captured"
                
        except Exception as e:
            self.logger.error(f"Error entering text and getting response: {e}")
            return f"Error: {str(e)}"
        
    def save_to_csv(self, question, response, reset_file=False):
        """
        Save question and response to CSV file with fixed 20 rows and Question, Answer, Score columns
        
        Args:
            question (str): The question asked
            response (str): The response received
            reset_file (bool): Whether to reset the file (clear all data)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create TestData directory if it doesn't exist
            test_data_dir = "TestData"
            os.makedirs(test_data_dir, exist_ok=True)
            
            file_path = os.path.join(test_data_dir, "chatresponse.csv")
            
            # If reset_file is True, create a fresh file
            if reset_file:
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    # Write header
                    writer.writerow(['Question', 'Answer', 'Score'])
                    
                    # Write 20 empty rows
                    for i in range(20):
                        writer.writerow(['', '', ''])
                print(f"CSV file reset: {file_path}")
            
            # Read existing data
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
            
            # Find first empty row (excluding header)
            empty_row_index = None
            for i in range(1, len(rows)):  # Skip header (index 0)
                if len(rows[i]) >= 3 and not rows[i][0].strip():  # Empty Question column
                    empty_row_index = i
                    break
            
            if empty_row_index is None:
                print("All 20 rows are filled. Cannot add more data.")
                return False
            
            # Update the empty row
            rows[empty_row_index][0] = question  # Question
            rows[empty_row_index][1] = response  # Answer
            rows[empty_row_index][2] = ""  # Score (empty for now)
            
            # Write back to file
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
            
            self.logger.info(f"Successfully saved to CSV: {question[:50]}...")
            print(f"Response saved to CSV file: {file_path}")
            print(f"Data added to row {empty_row_index}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {e}")
            print(f"Failed to save response to CSV: {e}")
            return False
        
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