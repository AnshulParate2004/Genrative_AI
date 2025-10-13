from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import create_react_agent
import datetime
from langchain.agents import tool
from langchain_community.tools import TavilySearchResults
load_dotenv()

llm =  ChatGoogleGenerativeAI(model="gemini-2.5-flash")

tavily_tool = TavilySearchResults(search_depth="basic")

@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S"):
    """ Returns the current date and time in the specified format """

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime(format)
    return formatted_time

tools = [get_system_time,tavily_tool]

react_prompt = hub.pull("hwchase17/react")

react_agent_runnable = create_react_agent(llm=llm, tools=tools, prompt = react_prompt)

