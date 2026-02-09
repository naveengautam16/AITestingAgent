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
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        test_params[key.strip()] = value.strip()
            
            print(f"Test parameters loaded successfully from {file_path}")
            return test_params
            
        except Exception as e:
            print(f"Error loading test data: {e}")
            return {}
    
    def load_questions_list(self, file_path="TestData/questionsList.txt"):
        """
        Load questions from questionsList.txt file
        
        Args:
            file_path (str): Path to the questions file
            
        Returns:
            list: List of questions
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                questions = [line.strip() for line in file.readlines() if line.strip()]
            
            print(f"Loaded {len(questions)} questions from {file_path}")
            return questions
            
        except Exception as e:
            print(f"Error loading questions list: {e}")
            return []

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
    
    # Load questions list
    questions = agent.load_questions_list()
    
    if not questions:
        print("Failed to load questions list. Exiting.")
        return
    
    try:
        print(f"\n--- Running Browser Test ---")
        print(f"URL: {test_params.get('url')}")
        print(f"Version: {test_params.get('version')}")
        print(f"Questions to process: {len(questions)}")
        
        # Setup browser (headless mode determined from test data)
        agent.browser_ops = BrowserOperations(test_params)
        await agent.browser_ops.setup_browser()
        
        # Open the URL
        url_opened = await agent.browser_ops.open_url(test_params.get('url'))
        if not url_opened:
            print("Failed to open URL or authentication required. Exiting.")
            return
        
        # Process each question
        for i, question in enumerate(questions, 1):
            print(f"\n--- Processing Question {i}/{len(questions)} ---")
            print(f"Question: {question}")
            
            # Enter question and get response
            response = await agent.browser_ops.enter_text_and_get_response(question, test_params.get('url'))
            
            # Save to CSV (reset file on first question)
            if response and response != "No response captured" and not response.startswith("Error:"):
                reset_file = (i == 1)  # Reset file only for the first question
                success = agent.browser_ops.save_to_csv(question, response, reset_file=reset_file)
                if success:
                    print(f"✅ Question {i} saved to CSV successfully!")
                else:
                    print(f"❌ Failed to save Question {i} to CSV")
            else:
                print(f"⚠️ Skipping Question {i} due to error or no response")
            
            # Wait a bit between questions to avoid overwhelming the chat
            if i < len(questions):  # Don't wait after the last question
                print("Waiting 3 seconds before next question...")
                await agent.browser_ops.wait(3000)
        
        print(f"\n--- All Questions Processed ---")
        print(f"Total questions processed: {len(questions)}")
        
        # Get final page information
        title = await agent.browser_ops.get_page_title()
        current_url = await agent.browser_ops.get_current_url()
        
        print(f"Final Page Title: {title}")
        print(f"Final URL: {current_url}")
        print("--- Test Completed ---")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Browser logs:")
        if hasattr(agent.browser_ops, 'page') and agent.browser_ops.page:
            print(await agent.browser_ops.page.content())
    
    finally:
        # Always close the browser
        if agent.browser_ops:
            await agent.browser_ops.close_browser()
            print("Browser closed successfully")

if __name__ == "__main__":
    asyncio.run(main())
