import asyncio
import logging
import os
from datetime import datetime
from commonMethods import BrowserOperations

class BrowserAgent:
    def __init__(self):
        """
        Initialize the Browser Agent
        """
        self.browser_ops = None
        self.test_params = None
        
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
        self.logger = logging.getLogger('BrowserAgent')
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
        
    def load_test_data(self, file_path="TestData/envTestData.txt"):
        """
        Load test parameters from text file
        
        Args:
            file_path (str): Path to the test data file
            
        Returns:
            dict: Dictionary containing test parameters
        """
        test_params = {}
        
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        # Add to test parameters
                        test_params[key] = value
            
            self.test_params = test_params
            # Initialize BrowserOperations with test parameters
            self.browser_ops = BrowserOperations(test_params)
            
            print(f"Test parameters loaded successfully from {file_path}")
            return test_params
            
        except FileNotFoundError:
            print(f"Test data file not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error reading test data file: {e}")
            return None

async def main():
    """
    Main execution function
    """
    # Create an instance of the Browser Agent
    agent = BrowserAgent()
    
    # Load test parameters
    test_params = agent.load_test_data()
    
    if not test_params:
        print("Failed to load test parameters. Exiting.")
        return
    
    try:
        print(f"\n--- Running Browser Test ---")
        print(f"URL: {test_params.get('url')}")
        print(f"Version: {test_params.get('version')}")
        
        # Setup browser (headless mode determined from test data)
        await agent.browser_ops.setup_browser()
        
        # Open the URL
        await agent.browser_ops.open_url(test_params.get('url'))
        
        # Enter "HI" in the input field and get response
        response = await agent.browser_ops.enter_text_and_get_response("HI")
        
        # Get page information
        title = await agent.browser_ops.get_page_title()
        current_url = await agent.browser_ops.get_current_url()
        
        print(f"Page Title: {title}")
        print(f"Current URL: {current_url}")
        print(f"Gemini Response: {response}")
        
        # Wait for default timeout
        await agent.browser_ops.wait(5000)
        
        print(f"--- Test Completed ---\n")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Ensure browser is closed
        await agent.browser_ops.close_browser()

if __name__ == "__main__":
    asyncio.run(main())
