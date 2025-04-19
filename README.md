Agentic AI Code Generator Bot
This project is an Agentic AI Code Generator Bot that autonomously generates, reviews, optimizes, and refines Python code snippets using OpenAI's GPT-4o model via the OpenAI API. Built with Streamlit for a user-friendly web interface and LangGraph for a stateful workflow, the bot enhances developer productivity by delivering context-aware, high-quality code tailored to user requests.
Features

Code Generation: Generates clean, functional Python code snippets based on user input (e.g., "Write a Python function to reverse a string").
Code Review: Automatically reviews code for correctness and clarity, approving or suggesting improvements.
Code Optimization: Enhances approved code for performance and readability.
Feedback Loop: Incorporates user or automated feedback to refine code, supporting continuous learning.
Web Interface: Streamlit front-end for easy interaction, with inputs for requests and feedback.
API-Based: Uses OpenAI's GPT-4o model, requiring an API key and internet access.

Prerequisites

Python 3.10 or higher
An OpenAI account with API key and GPT-4o access (set up at platform.openai.com)
Internet access for API calls

Installation

Clone the Repository:
git clone https://github.com/your-username/agentic-ai-code-generator-bot.git
cd agentic-ai-code-generator-bot


Create a .env File:

Create a .env file in the project root.
Add your OpenAI API key:OPENAI_API_KEY=your_openai_api_key


Obtain the key from platform.openai.com (ensure credits and GPT-4o access).


Install Dependencies:
pip install -r requirements.txt



Usage

Run the Streamlit App:
streamlit run code_generator_bot_gpt4_streamlit.py


Opens a browser at http://localhost:8501.


Interact with the Bot:

Enter a code request (e.g., "Write a Python function to reverse a string").
Optionally provide feedback (e.g., "Make it more efficient").
Click "Generate Code" to view the generated code, feedback, and iteration count.



Example Output
Input: "Write a Python function to reverse a string."Output:
def reverse_string(s):
    return s[::-1]

Feedback: NoneIterations: 1
File Structure
agentic-ai-code-generator-bot/
├── code_generator_bot_gpt4_streamlit.py  # Main script with Streamlit and LangGraph
├── .env                                  # Environment file for OPENAI_API_KEY (add your key)
├── requirements.txt                      # Dependency list
├── README.md                             # Project documentation

requirements.txt
langgraph
langchain
python-dotenv
sentence-transformers
streamlit
openai
optree>=0.13.0

Contributing
Contributions are welcome! Please:

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit changes (git commit -m 'Add your feature').
Push to the branch (git push origin feature/your-feature).
Open a pull request.

