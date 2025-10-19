from dotenv import load_dotenv
load_dotenv()

from langchain_core.agents import AgentFinish
from langgraph.graph import END, StateGraph
from react_state import AgentState
from agent_reason_runable import react_agent_runnable, tools
from react_state import AgentState


def reason_node(state: AgentState):
    agent_outcome = react_agent_runnable.invoke(state)
    return {"agent_outcome": agent_outcome}

def act_node(state: AgentState):
    agent_action = state["agent_outcome"]
    
    # Extract tool name and input from AgentAction
    tool_name = agent_action.tool
    tool_input = agent_action.tool_input
    
    # Find the matching tool function
    tool_function = None
    for tool in tools:
        if tool.name == tool_name:
            tool_function = tool
            break
    
    # Execute the tool with the input
    if tool_function:
        if isinstance(tool_input, dict):
            output = tool_function.invoke(**tool_input)
        else:
            output = tool_function.invoke(tool_input)
    else:
        output = f"Tool '{tool_name}' not found"
    
    return {"intermediate_steps": [(agent_action, str(output))]}



def should_continue(state: AgentState) -> str:
    if isinstance(state["agent_outcome"], AgentFinish):
        return END
    else:
        return ACT_NODE

REASON_NODE = "reason_node"
ACT_NODE = "act_node"

graph = StateGraph(AgentState)

graph.add_node(REASON_NODE, reason_node)
graph.set_entry_point(REASON_NODE)
graph.add_node(ACT_NODE, act_node)

graph.add_conditional_edges(
    REASON_NODE,
    should_continue,
)

graph.add_edge(ACT_NODE, REASON_NODE)

app = graph.compile()

result = app.invoke(
    {
        "input": "How many days ago was the latest SpaceX launch?", 
        "agent_outcome": None, 
        "intermediate_steps": []
    }
)
print(result)
print("=============================================================")
print(result["agent_outcome"].return_values["output"], "final result")