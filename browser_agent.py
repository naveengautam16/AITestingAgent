import asyncio
from commonMethods import BrowserOperations

# This class acts as the main controller/orchestrator for browser automation
# Operations include:
# - Loading test configuration from external data files (envTestData.txt)
# - Dynamic initialization of BrowserOperations with runtime parameters
# - Coordinating browser operations through BrowserOperations class
# - Managing test execution flow and parameter handling
# - Providing clean interface for running browser tests
# - Handling test data parsing and validation
# - Runtime browser mode configuration based on version parameter
class BrowserAgent:
    def __init__(self):
        """
        Initialize the Browser Agent using BrowserOperations from commonMethods
        """
        self.browser_ops = None
        self.test_params = None
        
    def load_test_data(self, file_path="TestData/envTestData.txt"):
        """
        Load test parameters from text file with key=value format
        
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
            
            print(f"Test parameters loaded successfully from {file_path}")
            self.test_params = test_params
            # Initialize BrowserOperations with test parameters
            self.browser_ops = BrowserOperations(test_params)
            return test_params
            
        except FileNotFoundError:
            print(f"Test data file not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error reading test data file: {e}")
            return None

async def main():
    """
    Example usage of the Browser Agent with test parameters
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
        
        # Use default timeout
        timeout = 5000
        
        # Setup browser (headless mode determined from test data)
        await agent.browser_ops.setup_browser()
        
        # Open the URL
        await agent.browser_ops.open_url(test_params.get('url'))
        
        # Get page information
        title = await agent.browser_ops.get_page_title()
        current_url = await agent.browser_ops.get_current_url()
        print(f"Page Title: {title}")
        print(f"Current URL: {current_url}")
        
        # Wait for default timeout
        await agent.browser_ops.wait(timeout)
        
        print(f"--- Test Completed ---\n")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Ensure browser is closed
        await agent.browser_ops.close_browser()

if __name__ == "__main__":
    asyncio.run(main())
