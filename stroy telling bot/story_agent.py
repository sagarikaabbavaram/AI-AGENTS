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
class StoryBotState(TypedDict):
    user_preferences: str
    generated_story: Optional[str]
    feedback: Optional[str]
    iteration: int
    error_message: Optional[str]
    is_approved: bool

# Node 1: Story Generator
def generate_story(state: StoryBotState) -> StoryBotState:
    prompt = PromptTemplate(
        input_variables=["preferences", "feedback"],
        template="Craft an engaging, coherent, and creative story based on these preferences: {preferences}. "
                 "Incorporate feedback if provided: {feedback}."
    )
    input_data = {
        "preferences": state["user_preferences"],
        "feedback": state["feedback"] or "No feedback."
    }
    prompt_text = prompt.format(**input_data)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=1000
        )
        state["generated_story"] = response.choices[0].message.content.strip()
    except Exception as e:
        state["error_message"] = f"Story generation failed: {str(e)}"
        return state
    state["iteration"] += 1
    state["is_approved"] = False
    state["error_message"] = None
    return state

# Node 2: Story Reviewer
def review_story(state: StoryBotState) -> StoryBotState:
    if state["error_message"]:
        return state
    prompt = PromptTemplate(
        input_variables=["story"],
        template="Review this story for coherence, engagement, and creativity: \n\n{story}\n\n"
                 "Return 'Approved' if no issues, else list specific issues."
    )
    prompt_text = prompt.format(story=state["generated_story"])
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
        state["error_message"] = f"Story review failed: {str(e)}"
    return state

# Node 3: Story Refiner
def refine_story(state: StoryBotState) -> StoryBotState:
    if state["is_approved"] and not state["error_message"]:
        prompt = PromptTemplate(
            input_variables=["story"],
            template="Refine this story to enhance its creativity, coherence, and engagement: \n\n{story}"
        )
        prompt_text = prompt.format(story=state["generated_story"])
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt_text}],
                max_tokens=1000
            )
            state["generated_story"] = response.choices[0].message.content.strip()
        except Exception as e:
            state["error_message"] = f"Story refinement failed: {str(e)}"
    return state

# Node 4: Feedback Handler
def handle_feedback(state: StoryBotState) -> StoryBotState:
    if state["is_approved"] or state["error_message"]:
        return state
    if state["iteration"] >= 3:
        state["feedback"] = "Max iterations reached."
        return state
    prompt = PromptTemplate(
        input_variables=["error_message"],
        template="Provide concise feedback to improve this story based on: {error_message}"
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
def decide_next_step(state: StoryBotState) -> str:
    if state["error_message"]:
        return END
    if state["is_approved"]:
        return "refine_story"
    if state["iteration"] >= 3:
        return END
    return "generate_story"

# Build the LangGraph workflow
workflow = StateGraph(StoryBotState)
workflow.add_node("generate_story", generate_story)
workflow.add_node("review_story", review_story)
workflow.add_node("refine_story", refine_story)
workflow.add_node("handle_feedback", handle_feedback)

# Add edges
workflow.add_edge("generate_story", "review_story")
workflow.add_edge("review_story", "handle_feedback")
workflow.add_edge("refine_story", END)
workflow.add_conditional_edges(
    "handle_feedback",
    decide_next_step,
    {
        "generate_story": "generate_story",
        "refine_story": "refine_story",
        END: END
    }
)

# Set entry point
workflow.set_entry_point("generate_story")

# Compile the graph
app = workflow.compile()

# Function to run the story generator
def run_story_generator(user_preferences: str, user_feedback: Optional[str] = None) -> StoryBotState:
    initial_state = StoryBotState(
        user_preferences=user_preferences,
        generated_story=None,
        feedback=user_feedback,
        iteration=0,
        error_message=None,
        is_approved=False
    )
    result = app.invoke(initial_state)
    return result

# Streamlit app
st.title("Agentic AI Storytelling Bot")
st.write("Enter story preferences to generate, review, and refine a creative narrative using GPT-4o model.")

# Input for user preferences
user_preferences = st.text_area("Story Preferences", placeholder="e.g., Genre: Fantasy, Theme: Adventure, Characters: A brave knight and a cunning dragon", height=100)

# Input for user feedback (optional)
user_feedback = st.text_area("Feedback (optional)", placeholder="e.g., Make the story more suspenseful", height=100)

# Button to generate story
if st.button("Generate Story"):
    if user_preferences:
        with st.spinner("Generating and refining story..."):
            try:
                result = run_story_generator(user_preferences, user_feedback)
                if result["error_message"]:
                    st.error(result["error_message"])
                else:
                    st.subheader("Generated Story")
                    st.write(result["generated_story"])
                    st.subheader("Feedback")
                    st.write(result["feedback"] or "No feedback needed.")
                    st.subheader("Iterations")
                    st.write(result["iteration"])
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.error("Please enter story preferences.")

if __name__ == "__main__":
    st.write("Run this app with: streamlit run storytelling_bot_gpt4_streamlit.py")