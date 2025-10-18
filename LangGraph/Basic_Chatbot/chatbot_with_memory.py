from typing import TypedDict, Annotated
from langgraph.graph import add_messages, StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


"""
Script Overview: Interactive Conversational AI with LangGraph and ChatGroq

1. State Definition:
   - BasicChatState holds chat messages in a list.
   - Annotated with add_messages to let the graph know these are conversation messages.

2. Language Model:
   - Uses ChatGroq (LLaMA 3.1) to generate AI responses.

3. StateGraph:
   - Manages workflow nodes and edges.
   - 'chatbot' node invokes the AI.
   - Connects to END to finish the workflow.

4. Memory/Checkpointer:
   - MemorySaver is used as a checkpointer to persist conversation history across multiple invocations.

5. Chatbot Function:
   - Takes current state messages.
   - Invokes the LLM to generate a response.
   - Returns updated state with the AI message.

6. Configuration:
   - Config dictionary allows passing extra parameters to the graph.
   - Example: 'thread_id' can track sessions or enable multi-threaded usage.

7. Interactive Loop:
   - Reads user input from console.
   - Exits on 'exit' or 'end'.
   - Invokes the graph with user input and prints AI responses.

8. Notes:
   - Currently, only the latest message is sent to the LLM unless messages are appended to preserve full chat history.
   - The setup can be extended with more nodes or dynamic branching for richer workflows.
"""


memory = MemorySaver()

llm = ChatGroq(model="llama-3.1-8b-instant")

class BasicChatState(TypedDict): 
    messages: Annotated[list, add_messages]

MAX_HISTORY = 10  # keep only last 10 messages

def chatbot(state: BasicChatState):
    # Invoke the AI on current messages
    new_message = llm.invoke(state["messages"])
    
    # Append the new message to state
    updated_messages = state["messages"] + [new_message]
    
    # Keep only the last MAX_HISTORY messages
    if len(updated_messages) > MAX_HISTORY:
        updated_messages = updated_messages[-MAX_HISTORY:]
    print ("Updated Messages in DB:", updated_messages)
    return {"messages": updated_messages}


graph = StateGraph(BasicChatState)

graph.add_node("chatbot", chatbot)

graph.add_edge("chatbot", END)

graph.set_entry_point("chatbot")

app = graph.compile(checkpointer=memory)

config = {"configurable": {
    "thread_id": 1
}}

while True: 
    user_input = input("User: ")
    if(user_input in ["exit", "end"]):
        break
    else: 
        result = app.invoke({
            "messages": [HumanMessage(content=user_input)]
        }, config=config)

        print("AI: " + result["messages"][-1].content)
