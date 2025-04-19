Agentic AI Bots: Code Generator and Storytelling
This repository contains two AI-powered projects: the Agentic AI Code Generator Bot and the Agentic AI Storytelling Bot, both leveraging OpenAI's GPT-4o model via the OpenAI API. Built with Streamlit for user-friendly web interfaces and LangGraph for stateful workflows, these bots enhance productivity and creativity by generating tailored code and narratives, respectively. They feature robust feedback loops for continuous learning, making them ideal for developers and storytellers.
Projects Overview
Agentic AI Code Generator Bot

Purpose: Autonomously generates, reviews, optimizes, and refines code snippets in any programming language (e.g., Python, Java, C++, JavaScript).
Features:
Generates functional code based on user requests and language selection.
Reviews code for correctness, optimizes approved code, and refines unapproved code using review feedback.
Supports multi-language code generation via user-specified input.



Agentic AI Storytelling Bot

Purpose: Crafts engaging, coherent, and creative narratives based on user preferences (e.g., genre, theme, characters).
Features:
Generates stories tailored to user inputs.
Reviews stories for coherence and engagement, refines approved stories, and improves unapproved ones using review feedback.
Enhances narratives through iterative refinement.



Prerequisites

Python 3.10 or higher
An OpenAI account with API key and GPT-4o access (platform.openai.com)
Internet access for API calls

Installation

Clone the Repository:
git clone https://github.com/your-username/agentic-ai-bots.git
cd agentic-ai-bots


Create a .env File:

Create a .env file in the project root.
Add your OpenAI API key:OPENAI_API_KEY=your_openai_api_key


Obtain the key from platform.openai.com.


Install Dependencies:
pip install -r requirements.txt



Usage
Code Generator Bot

Run the App:
streamlit run code_generator_bot_gpt4_streamlit.py


Opens a browser at http://localhost:8501.


Interact:

Select a programming language (e.g., Python, JavaScript) or specify another.
Enter a code request (e.g., "Write a function to reverse a string").
Optionally provide feedback (e.g., "Use a loop").
Click "Generate Code" to view the code, feedback, and iteration count.



Example Output:

Input: Request: "Write a function to reverse a string", Language: JavaScript, Feedback: "Use a loop"
Output:function reverseString(s) {
    if (typeof s !== 'string') {
        throw new Error('Input must be a string');
    }
    let result = '';
    for (let char of s) {
        result = char + result;
    }
    return result;
}

Feedback: "No feedback needed."Iterations: 1

Storytelling Bot

Run the App:
streamlit run storytelling_bot_gpt4_streamlit.py


Opens a browser at http://localhost:8501.


Interact:

Enter story preferences (e.g., "Genre: Fantasy, Theme: Adventure, Characters: A brave knight and a cunning dragon").
Optionally provide feedback (e.g., "Make the story more suspenseful").
Click "Generate Story" to view the story, feedback, and iteration count.



Example Output:

Input: Preferences: "Genre: Fantasy, Theme: Adventure, Characters: A brave knight and a cunning dragon", Feedback: "Add more suspense"
Output:In the misty peaks of Eldoria, Sir Alaric, a brave knight, faced Vyrnax, a cunning dragon, in a suspense-filled duel...

Feedback: "No feedback needed."Iterations: 1

File Structure
agentic-ai-bots/
├── code_generator_bot_gpt4_streamlit.py  # Code Generator Bot script
├── storytelling_bot_gpt4_streamlit.py    # Storytelling Bot script
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

