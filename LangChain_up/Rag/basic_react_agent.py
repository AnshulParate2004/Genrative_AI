from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.agents import initialize_agent, tool
from langchain_tavily import TavilySearch
import datetime
import os

# Load environment variables from .env
load_dotenv()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest")

# Print Tavily key to confirm it's loaded
print("Tavily key loaded:", os.getenv("TAVILY_API_KEY"))

# Initialize Tavily search
search_tool_instance = TavilySearch(search_depth="advanced")  # note spelling: "advanced"

# Wrap TavilySearch in a single-input tool
@tool
def tavily_search(query: str) -> str:
    """
    Perform a Tavily search for a single query string and return the results.
    """
    results = search_tool_instance.run(query)
    return results

# Tool to get system time
@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Returns the current date and time in the specified format.
    """
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime(format)
    return formatted_time

# Register tools
tools = [tavily_search, get_system_time]

# Initialize agent with ZeroShotAgent (single-input tools only)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

# Example invocation
query = "When was SpaceX's last launch and how many days ago was it?"
response = agent.invoke(query)

print("\nAgent response:\n", response)
