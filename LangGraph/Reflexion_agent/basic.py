from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from chains import generation_chain, reflection_chain

# Load environment variables
load_dotenv()

# -----------------------------
# Define State Schema
# -----------------------------
class TweetState(TypedDict):
    messages: List[HumanMessage]
    step: int

# -----------------------------
# Node Names
# -----------------------------
GENERATE = "generate"
REFLECT = "reflect"

# -----------------------------
# Node Functions
# -----------------------------
def generate_node(state: TweetState) -> TweetState:
    """
    Generates a tweet using generation_chain.
    Only keeps the last message in state.
    """
    messages = state["messages"]  # only latest message
    response = generation_chain.invoke({"messages": messages})

    new_message = HumanMessage(content=response.content)
    return {
        "messages": messages + [new_message],  # keep last + new
        "step": state["step"] + 1
    }

def reflect_node(state: TweetState) -> TweetState:
    """
    Reflects on the generated tweet using reflection_chain.
    Only keeps the last message in state.
    """
    messages = state["messages"]  # only latest message
    response = reflection_chain.invoke({"messages": messages})

    new_message = HumanMessage(content=response.content)
    return {
        "messages": messages + [new_message],  # keep last + new
        "step": state["step"] + 1
    }

# -----------------------------
# Build StateGraph
# -----------------------------
graph = StateGraph(TweetState)

graph.add_node(GENERATE, generate_node)
graph.add_node(REFLECT, reflect_node)
graph.set_entry_point(GENERATE)

# -----------------------------
# Conditional Transition Logic
# -----------------------------
def should_continue(state: TweetState):
    """
    Loop until we have more than 6 messages.
    """
    if len(state["messages"]) > 1:
        return END
    return REFLECT

graph.add_conditional_edges(GENERATE, should_continue)
graph.add_edge(REFLECT, GENERATE)

# Compile the graph
app = graph.compile()

# -----------------------------
# Run the graph
# -----------------------------
initial_state = {
    "messages": [HumanMessage(content="AI Agents taking over content creation")],
    "step": 0
}

final_state = app.invoke(initial_state)

# -----------------------------
# Display Final State
# -----------------------------
output_path = "final_conversation.txt"

with open(output_path, "w", encoding="utf-8") as f:
    f.write("=== Final Conversation ===\n\n")
    for i, msg in enumerate(final_state["messages"], 1):
        f.write(f"{i}. {msg.content}\n\n")

print(f"\n✅ Conversation saved to {output_path}")
