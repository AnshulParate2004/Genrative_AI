from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing import TypedDict

class State(TypedDict):
    text: str

def node_a(state: State): 
    print("Node A")
    print("Current text:", state["text"])
    return Command(
        goto="node_b", 
        update={
            "text": state["text"] + "a"
        }
    )

def node_b(state: State): 
    print("Node B")
    print("Current text:", state["text"])
    return Command(
        goto="node_c", 
        update={
            "text": state["text"] + "b"
        }
    )


def node_c(state: State): 
    print("Node C")
    print("Current text:", state["text"])
    return Command(
        goto=END, 
        update={
            "text": state["text"] + "c"
        }
    )

graph = StateGraph(State)

graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_node("node_c", node_c)

graph.set_entry_point("node_a")


app = graph.compile()

response = app.invoke({
    "text": ""
})

print("Final text" , response["text"]) 