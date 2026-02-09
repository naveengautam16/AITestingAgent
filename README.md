
🤖 **AI Chatbot Testing Framework - Auto-Detect & Test Any Chatbot**

### **Step 1: Setup**
pip install -r requirements.txt

### **Step 2: Configure**
Edit `TestData/envTestData.txt` and add the URL to test and Version (headless or non-headless)

### **Step 3: Add Questions**
Edit `TestData/questionsList.txt` and add list of questions to be tested.

### **Step 4: Run the test**
python3 browser_agent.py


The framework will:
1. **Auto-detect** your chatbot type from URL
2. **Find** input field, send button, and response field automatically
3. **Process** all questions and answers will be saved in "chatresponse.csv" file under test data folder



