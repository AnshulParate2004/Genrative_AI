from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel
from typing import List
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatGroq(model="llama-3.1-8b-instant")

# -----------------------------
# Define the State using Pydantic
# -----------------------------
class State(BaseModel):
    linkedin_topic: str
    generated_post: List[AIMessage] = []
    human_feedback: List[str] = []

# -----------------------------
# Model Node: Generates LinkedIn Post
# -----------------------------
def model(state: State):
    """Generate a LinkedIn post based on topic and human feedback."""

    print("[model] Generating content...")
    linkedin_topic = state.linkedin_topic
    feedback = state.human_feedback or ["No feedback yet"]

    prompt = f"""
LinkedIn Topic: {linkedin_topic}
Human Feedback: {feedback[-1] if feedback else "No feedback yet"}

Generate a structured and well-written LinkedIn post based on the given topic.
Consider previous human feedback to refine the response.
"""

    response = llm.invoke([
        SystemMessage(content="You are an expert LinkedIn content writer"),
        HumanMessage(content=prompt)
    ])

    generated_post = response.content
    print(f"[model_node] Generated post:\n{generated_post}\n")

    return {
        "generated_post": state.generated_post + [AIMessage(content=generated_post)],
        "human_feedback": state.human_feedback
    }

# -----------------------------
# Human Node: Collects Feedback
# -----------------------------
def human_node(state: State):
    """Human intervention node - loops back to model unless finished."""

    print("\n[human_node] Awaiting human feedback...")
    last_post = state.generated_post[-1].content if state.generated_post else "No post yet"

    user_feedback = interrupt({
        "generated_post": last_post,
        "message": "Provide feedback or type 'done' to finish"
    })

    print(f"[human_node] Received human feedback: {user_feedback}")

    if user_feedback.lower() == "done":
        return Command(update={"human_feedback": state.human_feedback + ["Finalized"]}, goto="end_node")

    # Otherwise, update feedback and loop back to model
    return Command(update={"human_feedback": state.human_feedback + [user_feedback]}, goto="model")

# -----------------------------
# End Node: Final Output
# -----------------------------
def end_node(state: State):
    print("\n[end_node] Process finished.")
    print("Final Generated Post:", state.generated_post[-1].content)
    print("Final Human Feedback:", state.human_feedback[-1])
    return {"generated_post": state.generated_post, "human_feedback": state.human_feedback}

# -----------------------------
# Build the StateGraph
# -----------------------------
graph = StateGraph(State)
graph.add_node("model", model)
graph.add_node("human_node", human_node)
graph.add_node("end_node", end_node)

graph.set_entry_point("model")
graph.add_edge(START, "model")
graph.add_edge("model", "human_node")
graph.set_finish_point("end_node")

# -----------------------------
# Compile the graph with memory saver
# -----------------------------
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# Thread config
thread_config = {"configurable": {"thread_id": uuid.uuid4()}}

# -----------------------------
# Initialize state and run
# -----------------------------
linkedin_topic = input("Enter your LinkedIn topic: ")
initial_state = State(
    linkedin_topic=linkedin_topic,
    generated_post=[],
    human_feedback=[]
)

# Stream execution and handle human feedback
for chunk in app.stream(initial_state.model_dump(), config=thread_config):
    for node_id, value in chunk.items():
        if node_id == "__interrupt__":
            while True:
                user_feedback = input("Provide feedback (or type 'done' when finished): ")
                app.invoke(Command(resume=user_feedback), config=thread_config)
                if user_feedback.lower() == "done":
                    break
