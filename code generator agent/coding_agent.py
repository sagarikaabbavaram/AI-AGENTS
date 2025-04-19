from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from langchain.prompts import PromptTemplate
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import os

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Please set OPENAI_API_KEY in .env file.")
    st.stop()
client = OpenAI(api_key=api_key)

# Define the state to track the workflow
class CodeBotState(TypedDict):
    user_request: str
    language: str
    generated_code: Optional[str]
    feedback: Optional[str]
    review_issues: Optional[str]
    iteration: int
    error_message: Optional[str]
    is_approved: bool

# Node 1: Code Generator
def generate_code(state: CodeBotState) -> CodeBotState:
    prompt = PromptTemplate(
        input_variables=["language", "request", "feedback"],
        template="Generate a clean, functional {language} code snippet for: {request}. "
                 "Incorporate feedback if provided: {feedback}."
    )
    input_data = {
        "language": state["language"],
        "request": state["user_request"],
        "feedback": state["feedback"] or "No feedback."
    }
    prompt_text = prompt.format(**input_data)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=500
        )
        state["generated_code"] = response.choices[0].message.content.strip()
    except Exception as e:
        state["error_message"] = f"Code generation failed: {str(e)}"
        return state
    state["iteration"] += 1
    state["error_message"] = None
    return state

# Node 2: Code Reviewer
def review_code(state: CodeBotState) -> CodeBotState:
    if state["error_message"]:
        return state
    prompt = PromptTemplate(
        input_variables=["language", "code"],
        template="Review this {language} code for correctness and clarity: \n\n{code}\n\n"
                 "Return 'Approved' if no issues, else list specific issues."
    )
    prompt_text = prompt.format(language=state["language"], code=state["generated_code"])
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=500
        )
        review_result = response.choices[0].message.content.strip()
        state["is_approved"] = "Approved" in review_result
        state["review_issues"] = None if state["is_approved"] else review_result
    except Exception as e:
        state["error_message"] = f"Code review failed: {str(e)}"
    return state

# Node 3: Code Optimizer
def optimize_code(state: CodeBotState) -> CodeBotState:
    if state["error_message"]:
        return state
    prompt = PromptTemplate(
        input_variables=["language", "code"],
        template="Optimize this {language} code for performance and readability: \n\n{code}"
    )
    prompt_text = prompt.format(language=state["language"], code=state["generated_code"])
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=500
        )
        state["generated_code"] = response.choices[0].message.content.strip()
    except Exception as e:
        state["error_message"] = f"Code optimization failed: {str(e)}"
    return state

# Node 4: Handle Reviews
def handle_reviews(state: CodeBotState) -> CodeBotState:
    if state["error_message"]:
        return state
    if state["iteration"] >= 3:
        state["feedback"] = "Max iterations reached."
        return state
    state["feedback"] = state["review_issues"] or "No specific issues provided."
    return state

# Conditional edge decision for review_code
def decide_review_next_step(state: CodeBotState) -> str:
    if state["error_message"]:
        return END
    if state["is_approved"]:
        return "optimize_code"
    return "handle_reviews"

# Conditional edge decision for handle_reviews
def decide_reviews_next_step(state: CodeBotState) -> str:
    if state["error_message"]:
        return END
    if state["iteration"] >= 3:
        return END
    return "generate_code"

# Build the LangGraph workflow
workflow = StateGraph(CodeBotState)
workflow.add_node("generate_code", generate_code)
workflow.add_node("review_code", review_code)
workflow.add_node("optimize_code", optimize_code)
workflow.add_node("handle_reviews", handle_reviews)

# Add edges
workflow.add_edge("generate_code", "review_code")
workflow.add_edge("optimize_code", END)
workflow.add_conditional_edges(
    "review_code",
    decide_review_next_step,
    {
        "optimize_code": "optimize_code",
        "handle_reviews": "handle_reviews",
        END: END
    }
)
workflow.add_conditional_edges(
    "handle_reviews",
    decide_reviews_next_step,
    {
        "generate_code": "generate_code",
        END: END
    }
)

# Set entry point
workflow.set_entry_point("generate_code")

# Compile the graph
app = workflow.compile()

# Function to run the code generator
def run_code_generator(user_request: str, language: str, user_feedback: Optional[str] = None) -> CodeBotState:
    initial_state = CodeBotState(
        user_request=user_request,
        language=language,
        generated_code=None,
        feedback=user_feedback,
        review_issues=None,
        iteration=0,
        error_message=None,
        is_approved=False
    )
    result = app.invoke(initial_state)
    return result

# Streamlit app
st.title("Agentic AI Code Generator Bot")
st.write("Enter a coding request and select a programming language to generate, review, and optimize code using GPT-4o model.")

# Input for programming language
language = st.selectbox("Programming Language", ["Python", "Java", "C++", "JavaScript", "Other (specify)"])
if language == "Other (specify)":
    language = st.text_input("Specify Language", placeholder="e.g., Ruby")

# Input for user request
user_request = st.text_input("Code Request", placeholder="e.g., Write a function to reverse a string")

# Input for user feedback (optional)
user_feedback = st.text_area("Feedback (optional)", placeholder="e.g., Make it more efficient", height=100)

# Button to generate code
if st.button("Generate Code"):
    if user_request and language:
        with st.spinner("Generating and optimizing code..."):
            try:
                result = run_code_generator(user_request, language, user_feedback)
                if result["error_message"]:
                    st.error(result["error_message"])
                else:
                    st.subheader("Generated Code")
                    st.code(result["generated_code"], language=language.lower())
                    st.subheader("Feedback")
                    st.write(result["feedback"] or "No feedback needed.")
                    st.subheader("Iterations")
                    st.write(result["iteration"])
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.error("Please enter a code request and select a programming language.")

if __name__ == "__main__":
    st.write("Run this app with: streamlit run code_generator_bot_gpt4_streamlit.py")
