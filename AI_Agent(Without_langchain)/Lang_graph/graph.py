from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
import os
import json

# Load environment variables
load_dotenv()

# -----------------------------
# Schema
# -----------------------------
class DetectCallResponse(BaseModel):
    is_question_ai: bool

# -----------------------------
# Groq client
# -----------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# -----------------------------
# Define state structure
# -----------------------------
class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool

# -----------------------------
# Node functions
# -----------------------------
def detect_query(state: State):
    user_message = state.get("user_message")

    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to detect if the user's query is related
    to a coding question or not.
    
    Respond ONLY in JSON format following this schema:
    {
        "is_question_ai": boolean
    }
    """

    result = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        response_format={
            "type": "json_object",
            "name": "DetectCallResponse",
            "schema": {
                "type": "object",
                "properties": {
                    "is_question_ai": {"type": "boolean"}
                },
                "required": ["is_question_ai"]
            }
        }
    )

    # Parse content safely
    message_content = result.choices[0].message.content
    if isinstance(message_content, str):
        message_content = json.loads(message_content)

    parsed = DetectCallResponse(**message_content)

    state["is_coding_question"] = parsed.is_question_ai
    print("State is :",state)
    return state


def route_edge(state: State):
    # Must return a dict mapping the next node name to state
    if state["is_coding_question"]:
        return {"solve_coding_question": state}
    else:
        return {"solve_simple_questions": state}

def solve_coding_question(state: State):
    state["ai_message"] = "Here is your code question answer."
    return state

def solve_simple_questions(state: State):
    state["ai_message"] = "Please ask a coding-related question."
    return state

# -----------------------------
# Build the graph
# -----------------------------
graph_builder = StateGraph(State)

graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("route_edge", route_edge)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_questions", solve_simple_questions)

# Add edges
graph_builder.add_edge(START, "detect_query")
graph_builder.add_edge("detect_query", "route_edge")
graph_builder.add_conditional_edges("route_edge", route_edge)
graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_questions", END)

graph = graph_builder.compile()

# -----------------------------
# Run the graph
# -----------------------------
def call_graph():
    state = {
        "user_message": "tell me fuctions in c?",
        "ai_message": "",
        "is_coding_question": False
    }
    result = graph.invoke(state)
    print("Final Result:", result)

if __name__ == "__main__":
    call_graph()
