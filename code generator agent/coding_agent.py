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
    generated_code: Optional[str]
    feedback: Optional[str]
    iteration: int
    error_message: Optional[str]
    is_approved: bool

# Node 1: Code Generator
def generate_code(state: CodeBotState) -> CodeBotState:
    prompt = PromptTemplate(
        input_variables=["request", "feedback"],
        template="Generate a clean, functional Python code snippet for: {request}. "
                 "Incorporate feedback if provided: {feedback}."
    )
    input_data = {
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
    state["is_approved"] = False
    state["error_message"] = None
    return state

# Node 2: Code Reviewer
def review_code(state: CodeBotState) -> CodeBotState:
    if state["error_message"]:
        return state
    prompt = PromptTemplate(
        input_variables=["code"],
        template="Review this Python code for correctness and clarity: \n\n{code}\n\n"
                 "Return 'Approved' if no issues, else list specific issues."
    )
    prompt_text = prompt.format(code=state["generated_code"])
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=500
        )
        review_result = response.choices[0].message.content.strip()
        state["is_approved"] = "Approved" in review_result
        state["error_message"] = None if state["is_approved"] else review_result
    except Exception as e:
        state["error_message"] = f"Code review failed: {str(e)}"
    return state

# Node 3: Code Optimizer
def optimize_code(state: CodeBotState) -> CodeBotState:
    if state["is_approved"] and not state["error_message"]:
        prompt = PromptTemplate(
            input_variables=["code"],
            template="Optimize this Python code for performance and readability: \n\n{code}"
        )
        prompt_text = prompt.format(code=state["generated_code"])
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

# Node 4: Feedback Handler
def handle_feedback(state: CodeBotState) -> CodeBotState:
    if state["is_approved"] or state["error_message"]:
        return state
    if state["iteration"] >= 3:
        state["feedback"] = "Max iterations reached."
        return state
    prompt = PromptTemplate(
        input_variables=["error_message"],
        template="Provide concise feedback to improve this code based on: {error_message}"
    )
    prompt_text = prompt.format(error_message=state["error_message"])
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=500
        )
        state["feedback"] = response.choices[0].message.content.strip()
    except Exception as e:
        state["error_message"] = f"Feedback generation failed: {str(e)}"
    return state

# Conditional edge to decide next step
def decide_next_step(state: CodeBotState) -> str:
    if state["error_message"]:
        return END
    if state["is_approved"]:
        return "optimize_code"
    if state["iteration"] >= 3:
        return END
    return "generate_code"

# Build the LangGraph workflow
workflow = StateGraph(CodeBotState)
workflow.add_node("generate_code", generate_code)
workflow.add_node("review_code", review_code)
workflow.add_node("optimize_code", optimize_code)
workflow.add_node("handle_feedback", handle_feedback)

# Add edges
workflow.add_edge("generate_code", "review_code")
workflow.add_edge("review_code", "handle_feedback")
workflow.add_edge("optimize_code", END)
workflow.add_conditional_edges(
    "handle_feedback",
    decide_next_step,
    {
        "generate_code": "generate_code",
        "optimize_code": "optimize_code",
        END: END
    }
)

# Set entry point
workflow.set_entry_point("generate_code")

# Compile the graph
app = workflow.compile()

# Function to run the code generator
def run_code_generator(user_request: str, user_feedback: Optional[str] = None) -> CodeBotState:
    initial_state = CodeBotState(
        user_request=user_request,
        generated_code=None,
        feedback=user_feedback,
        iteration=0,
        error_message=None,
        is_approved=False
    )
    result = app.invoke(initial_state)
    return result

# Streamlit app
st.title("Agentic AI Code Generator Bot")
st.write("Enter a coding request to generate, review, and optimize Python code using GPT-4o model.")

# Input for user request
user_request = st.text_input("Code Request", placeholder="e.g., Write a Python function to reverse a string")

# Input for user feedback (optional)
user_feedback = st.text_area("Feedback (optional)", placeholder="e.g., Make it more efficient", height=100)

# Button to generate code
if st.button("Generate Code"):
    if user_request:
        with st.spinner("Generating and optimizing code..."):
            try:
                result = run_code_generator(user_request, user_feedback)
                if result["error_message"]:
                    st.error(result["error_message"])
                else:
                    st.subheader("Generated Code")
                    st.code(result["generated_code"], language="python")
                    st.subheader("Feedback")
                    st.write(result["feedback"] or "No feedback needed.")
                    st.subheader("Iterations")
                    st.write(result["iteration"])
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.error("Please enter a code request.")

if __name__ == "__main__":
    st.write("Run this app with: streamlit run code_generator_bot_gpt4_streamlit.py")