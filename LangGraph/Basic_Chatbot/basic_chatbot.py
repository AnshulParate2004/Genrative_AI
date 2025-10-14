from typing import TypedDict,Annotated,Union
from langgraph.graph import add_messages, StateGraph,END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

class BasicChatState(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: BasicChatState):
    return{
        "messages":llm.invoke(state["messages"])
    }

graph = StateGraph(BasicChatState)

graph.add_node("chatbot",chatbot)
graph.set_entry_point("chatbot")
graph.add_edge("chatbot",END)

app =graph.compile()

while True:
    user_input = input("User: ")
    if(user_input in ["exit","end"]):
        break 
    else:
        result = app.invoke({
            "messages":[HumanMessage(content=user_input)]
        })
        print("Ai: ",result["messages"][-1].content)