import asyncio
import logging
import os
import csv
from datetime import datetime
from playwright.async_api import async_playwright
from locators.chatbot_locators import ChatbotLocators, LocatorUtils

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
                sign_in_button = await self.page.query_selector(ChatbotLocators.SIGN_IN_SELECTORS[0])
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
        
    async def enter_text_and_get_response(self, text, url=None):
        """
        Enter text in the input field and get response from the AI using self-healing
        
        Args:
            text (str): Text to enter in the input field
            url (str): URL for context-specific locators
            
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
            
            # Use self-healing to find input field with URL context
            input_field = await self.find_element_with_healing('input', url=url)
            
            if not input_field:
                raise Exception("Could not find any visible input field with self-healing")
            
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
            
            # Use self-healing to find send button with URL context
            send_button = await self.find_element_with_healing('send', url=url)
            
            if send_button:
                print("Found send button, clicking...")
                await send_button.click()
                send_found = True
            else:
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
            
        except Exception as e:
            print(f"Error in send button handling: {e}")
            raise
        
        try:
            # Wait for response
            print("Waiting for AI response...")
            await self.page.wait_for_timeout(10000)  # Increased wait time to 10 seconds
            
            # Check if page is still active
            if self.page.is_closed():
                raise Exception("Page was closed while waiting for response")
            
            # Additional wait to ensure response is fully loaded
            print("Ensuring response is fully loaded...")
            await self.page.wait_for_timeout(2000)
            
            print(f"Trying to capture response...")
            response_text = ""
            
            # Use self-healing to find response elements with URL context
            response_elements = []
            
            # Try to get all possible response elements using primary locator first
            primary_response_locator = LocatorUtils.get_primary_response_locator(url)
            primary_elements = await self.page.query_selector_all(primary_response_locator)
            
            if primary_elements:
                response_elements.extend(primary_elements)
            
            # If primary doesn't work, try all fallbacks
            if len(response_elements) < 2:  # Need at least 2 elements for Q&A
                fallbacks = LocatorUtils.get_fallback_locators(primary_response_locator, 'response', url)
                for fallback_locator in fallbacks:
                    try:
                        fallback_elements = await self.page.query_selector_all(fallback_locator)
                        if fallback_elements:
                            response_elements.extend(fallback_elements)
                            break  # Stop after first successful fallback
                    except:
                        continue
            
            # Filter out placeholder text and UI elements
            placeholder_texts = [
                "Enter to send",
                "Shift + Enter to newline",
                "Enter to send; Shift + Enter to newline",
                "Type a message",
                "Type your message",
                "Ask me anything",
                "Send a message",
                "Enter your prompt",
                "Start typing..."
            ]
            
            ui_elements = [
                "Expand menu", "Use microphone", "New chat", "Edit prompt",
                "Stop response", "Continue", "Regenerate", "Copy", "Share",
                "Send", "Submit", "Clear", "Delete", "Edit"
            ]
            
            # Find the most recent AI response (after sending current question)
            if response_elements:
                # Get all visible elements with substantial text
                valid_responses = []
                for element in response_elements:
                    try:
                        text = await element.text_content()
                        visible = await element.is_visible()
                        
                        if text and visible and len(text.strip()) > 20:
                            # Filter out placeholder text and UI elements
                            text_clean = text.strip()
                            is_placeholder = any(placeholder in text_clean for placeholder in placeholder_texts)
                            is_ui_element = any(ui in text_clean for ui in ui_elements)
                            
                            if not is_placeholder and not is_ui_element:
                                # Check if this is likely an AI response (not user message)
                                is_user_message = text_clean.lower() == text.lower()  # Exact match to user question
                                is_short_response = len(text_clean) < 30  # Very short, likely UI text
                                
                                if not is_user_message and not is_short_response:
                                    # Get element position to find the most recent one
                                    bounding_box = await element.bounding_box()
                                    valid_responses.append({
                                        'element': element,
                                        'text': text_clean,
                                        'length': len(text_clean),
                                        'y_position': bounding_box['y'] if bounding_box else 0
                                    })
                                    print(f"  Valid AI response found: {text_clean[:50]}... (y: {bounding_box['y'] if bounding_box else 0})")
                    except:
                        pass
                
                # Get the response with the lowest y position (most recent/bottom of page)
                if valid_responses:
                    # Sort by y position (higher y = lower on page = more recent)
                    valid_responses.sort(key=lambda x: x['y_position'], reverse=True)
                    latest_response = valid_responses[0]['text']
                    response_text = latest_response
                    print(f"Found most recent AI response (y_position: {valid_responses[0]['y_position']})!")
                    print(f"Response: {response_text[:100]}...")
            
            # If still no response, try to get all text content and parse
            if not response_text:
                print("Trying to extract response from page content...")
                try:
                    # Wait a bit more for the response to appear
                    await self.page.wait_for_timeout(3000)
                    
                    # Get all text content
                    page_text = await self.page.evaluate('() => document.body.innerText')
                    print(f"Page text length: {len(page_text)}")
                    
                    # Look for text that appears after our question
                    if text in page_text:
                        parts = page_text.split(text)
                        if len(parts) > 1:
                            # Get text after our question and clean it up
                            after_question = parts[-1].strip()
                            lines = after_question.split('\n')
                            
                            # Find the longest meaningful line (likely AI response)
                            valid_lines = []
                            for line in lines:
                                line_clean = line.strip()
                                if line_clean and len(line_clean) > 20:
                                    # Filter out placeholder text and UI elements
                                    is_placeholder = any(placeholder in line_clean for placeholder in placeholder_texts)
                                    is_ui_element = any(ui in line_clean for ui in ui_elements)
                                    is_user_message = line_clean.lower() == text.lower()
                                    is_short_response = len(line_clean) < 30
                                    
                                    if not is_placeholder and not is_ui_element and not is_user_message and not is_short_response:
                                        valid_lines.append({
                                            'text': line_clean,
                                            'length': len(line_clean)
                                        })
                            
                            # Get the longest line (most likely AI response)
                            if valid_lines:
                                valid_lines.sort(key=lambda x: x['length'], reverse=True)
                                response_text = valid_lines[0]['text']
                                print(f"Extracted best AI response from page content: {response_text[:100]}...")
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
        
    async def find_element_with_healing(self, locator_type, primary_locator=None, url=None):
        """
        Find element using self-healing logic with URL-based auto-detection
        
        Args:
            locator_type (str): Type of element ('input', 'send', 'response')
            primary_locator (str): Primary locator to try first (optional)
            url (str): URL for context-specific locators
            
        Returns:
            element: Found element or None if not found
        """
        try:
            # If no primary locator provided, get the URL-based one
            if not primary_locator:
                primary_locator = LocatorUtils.get_primary_input_locator(url) if locator_type == 'input' else \
                           LocatorUtils.get_primary_send_button_locator(url) if locator_type == 'send' else \
                           LocatorUtils.get_primary_response_locator(url)
            
            print(f"🎯 Trying primary {locator_type} locator: {primary_locator}")
            
            # Try primary locator first
            elements = await self.page.query_selector_all(primary_locator)
            if elements:
                for element in elements:
                    try:
                        visible = await element.is_visible()
                        if visible:
                            print(f"✅ Primary {locator_type} locator found and visible!")
                            return element
                    except:
                        continue
            
            print(f"❌ Primary {locator_type} locator failed, trying fallbacks...")
            
            # Get fallback locators with URL context
            fallbacks = LocatorUtils.get_fallback_locators(primary_locator, locator_type, url)
            
            # Try each fallback locator
            for i, fallback_locator in enumerate(fallbacks, 1):
                print(f"🔄 Fallback {i}/{len(fallbacks)}: {fallback_locator}")
                try:
                    elements = await self.page.query_selector_all(fallback_locator)
                    if elements:
                        for element in elements:
                            try:
                                visible = await element.is_visible()
                                if visible:
                                    print(f"✅ Fallback {locator_type} locator found: {fallback_locator}")
                                    return element
                            except:
                                continue
                except Exception as e:
                    print(f"⚠️ Fallback {i} failed: {e}")
                    continue
            
            # If all specific locators fail, try generic fallbacks
            print(f"❌ All {locator_type} locators failed, trying generic approach...")
            generic_fallbacks = LocatorUtils.get_generic_fallbacks()
            
            for element in await self.page.query_selector_all(', '.join(generic_fallbacks)):
                try:
                    visible = await element.is_visible()
                    if visible:
                        print(f"✅ Generic {locator_type} element found!")
                        return element
                except:
                    continue
            
            print(f"❌ No {locator_type} element found with any locator")
            return None
            
        except Exception as e:
            print(f"💥 Self-healing failed for {locator_type}: {e}")
            return None
    
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