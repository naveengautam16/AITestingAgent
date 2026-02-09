"""
Locators for Chatbot Interface
This file contains all the CSS selectors and locators used to interact with the chatbot interface
"""

class ChatbotLocators:
    """
    Locators for various Chatbot interfaces
    Auto-detection based on URL patterns
    """
    
    # URL-based locator configurations
    URL_PATTERNS = {
        'easemate': {
            'url_patterns': ['easemate.ai', 'ease-mate.ai'],
            'input_primary': 'textarea[placeholder*="Ask"]',
            'send_primary': 'button[aria-label*="Send"]',
            'response_primary': '.chat-message'
        },
        'gemini': {
            'url_patterns': ['gemini.google.com', 'bard.google.com'],
            'input_primary': 'div[contenteditable="true"]',
            'send_primary': 'button[aria-label*="Send"]',
            'response_primary': '.response-content'
        },
        'chatgpt': {
            'url_patterns': ['chat.openai.com', 'chatgpt.com'],
            'input_primary': '#prompt-textarea',
            'send_primary': 'button[data-testid="send-button"]',
            'response_primary': '.markdown'
        },
        'claude': {
            'url_patterns': ['claude.ai'],
            'input_primary': 'div[contenteditable="true"]',
            'send_primary': 'button[aria-label*="Send"]',
            'response_primary': '.font-claude-message'
        },
        'default': {
            'url_patterns': [],  # Catch-all
            'input_primary': 'textarea[placeholder*="Ask"]',
            'send_primary': 'button[aria-label*="Send"]',
            'response_primary': '.chat-message'
        }
    }
    
    # Universal fallback locators (work across most chatbots)
    UNIVERSAL_INPUT_SELECTORS = [
        'textarea[placeholder*="Ask"]',
        'textarea[placeholder*="message"]',
        'textarea[placeholder*="Message"]',
        'textarea[placeholder*="Type"]',
        'textarea[placeholder*="type"]',
        'input[type="text"]',
        'div[contenteditable="true"]',
        '[contenteditable="true"]',
        '[role="textbox"]',
        'textarea',
        '.input-field',
        '.chat-input',
        '#message-input',
        'input[placeholder*="Type"]',
        'div[role="textbox"]'
    ]
    
    UNIVERSAL_SEND_SELECTORS = [
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
    
    UNIVERSAL_RESPONSE_SELECTORS = [
        '.chat-message',
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
    
    # Legacy selectors for backward compatibility
    INPUT_FIELD_SELECTORS = UNIVERSAL_INPUT_SELECTORS
    SEND_BUTTON_SELECTORS = UNIVERSAL_SEND_SELECTORS
    RESPONSE_SELECTORS = UNIVERSAL_RESPONSE_SELECTORS
    
    # Authentication locators
    SIGN_IN_SELECTORS = [
        'button:has-text("Sign in")',
        'a:has-text("Sign in")'
    ]
    
    # Generic input fallback selectors
    GENERIC_INPUT_SELECTORS = [
        'input',
        'textarea', 
        '[contenteditable="true"]',
        '[role="textbox"]'
    ]


class LocatorUtils:
    """
    Utility methods for working with locators
    """
    
    @staticmethod
    def detect_chatbot_type(url):
        """
        Auto-detect chatbot type based on URL
        
        Args:
            url (str): The URL of the chatbot
            
        Returns:
            str: Detected chatbot type ('easemate', 'gemini', 'chatgpt', 'claude', 'default')
        """
        url_lower = url.lower()
        
        for chatbot_type, config in ChatbotLocators.URL_PATTERNS.items():
            for pattern in config['url_patterns']:
                if pattern in url_lower:
                    print(f"🎯 Auto-detected chatbot type: {chatbot_type}")
                    return chatbot_type
        
        return 'default'
    
    @staticmethod
    def get_primary_input_locator(url=None):
        """Get primary input locator based on URL or default"""
        if url:
            chatbot_type = LocatorUtils.detect_chatbot_type(url)
            config = ChatbotLocators.URL_PATTERNS.get(chatbot_type, ChatbotLocators.URL_PATTERNS['default'])
            return config['input_primary']
        return ChatbotLocators.URL_PATTERNS['default']['input_primary']
    
    @staticmethod
    def get_primary_send_button_locator(url=None):
        """Get primary send button locator based on URL or default"""
        if url:
            chatbot_type = LocatorUtils.detect_chatbot_type(url)
            config = ChatbotLocators.URL_PATTERNS.get(chatbot_type, ChatbotLocators.URL_PATTERNS['default'])
            return config['send_primary']
        return ChatbotLocators.URL_PATTERNS['default']['send_primary']
    
    @staticmethod
    def get_primary_response_locator(url=None):
        """Get primary response locator based on URL or default"""
        if url:
            chatbot_type = LocatorUtils.detect_chatbot_type(url)
            config = ChatbotLocators.URL_PATTERNS.get(chatbot_type, ChatbotLocators.URL_PATTERNS['default'])
            return config['response_primary']
        return ChatbotLocators.URL_PATTERNS['default']['response_primary']
    
    @staticmethod
    def get_all_locators():
        """Get all locator groups as a dictionary"""
        return {
            'input_fields': ChatbotLocators.UNIVERSAL_INPUT_SELECTORS,
            'send_buttons': ChatbotLocators.UNIVERSAL_SEND_SELECTORS,
            'responses': ChatbotLocators.UNIVERSAL_RESPONSE_SELECTORS,
            'sign_in': ChatbotLocators.SIGN_IN_SELECTORS,
            'generic_inputs': ChatbotLocators.GENERIC_INPUT_SELECTORS
        }
    
    @staticmethod
    def get_fallback_locators(primary_locator, locator_type, url=None):
        """
        Get fallback locators when primary locator fails
        
        Args:
            primary_locator (str): The primary locator that failed
            locator_type (str): Type of locator ('input', 'send', 'response')
            url (str): URL for context-specific fallbacks
            
        Returns:
            list: List of fallback locators to try
        """
        all_locators = LocatorUtils.get_all_locators()
        
        if locator_type == 'input':
            fallbacks = all_locators['input_fields']
        elif locator_type == 'send':
            fallbacks = all_locators['send_buttons']
        elif locator_type == 'response':
            fallbacks = all_locators['responses']
        else:
            return []
        
        # Remove the primary locator from fallbacks if it exists
        if primary_locator in fallbacks:
            fallbacks.remove(primary_locator)
        
        return fallbacks
    
    @staticmethod
    def get_generic_fallbacks():
        """Get generic fallback locators for any element type"""
        return ChatbotLocators.GENERIC_INPUT_SELECTORS
