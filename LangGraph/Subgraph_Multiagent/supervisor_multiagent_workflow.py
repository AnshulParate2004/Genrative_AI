from typing import Annotated, Sequence, List, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import create_react_agent
from IPython.display import Image, display
from dotenv import load_dotenv
from langchain_experimental.tools import PythonREPLTool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

tavily_search = TavilySearchResults(max_results=2)
python_repl_tool = PythonREPLTool()

# python_repl_tool.invoke("x = 5; print(x)") # '5\n'

class Supervisor(BaseModel):
    next: Literal["enhancer", "researcher", "coder"] = Field(
        description="Determines which specialist to activate next in the workflow sequence: "
                    "'enhancer' when user input requires clarification, expansion, or refinement, "
                    "'researcher' when additional facts, context, or data collection is necessary, "
                    "'coder' when implementation, computation, or technical problem-solving is required."
    )
    reason: str = Field(
        description="Detailed justification for the routing decision, explaining the rationale behind selecting the particular specialist and how this advances the task toward completion."
    )

def supervisor_node(state: MessagesState) -> Command[Literal["enhancer", "researcher", "coder"]]:

    system_prompt = ('''

        You are a workflow supervisor managing a team of three specialized agents: Prompt Enhancer, Researcher, and Coder. Your role is to orchestrate the workflow by selecting the most appropriate next agent based on the current state and needs of the task. Provide a clear, concise rationale for each decision to ensure transparency in your decision-making process.

        **Team Members**:
        1. **Prompt Enhancer**: Always consider this agent first. They clarify ambiguous requests, improve poorly defined queries, and ensure the task is well-structured before deeper processing begins.
        2. **Researcher**: Specializes in information gathering, fact-finding, and collecting relevant data needed to address the user's request.
        3. **Coder**: Focuses on technical implementation, calculations, data analysis, algorithm development, and coding solutions.

        **Your Responsibilities**:
        1. Analyze each user request and agent response for completeness, accuracy, and relevance.
        2. Route the task to the most appropriate agent at each decision point.
        3. Maintain workflow momentum by avoiding redundant agent assignments.
        4. Continue the process until the user's request is fully and satisfactorily resolved.

        Your objective is to create an efficient workflow that leverages each agent's strengths while minimizing unnecessary steps, ultimately delivering complete and accurate solutions to user requests.

    ''')

    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]

    response = llm.with_structured_output(Supervisor).invoke(messages)

    goto = response.next
    reason = response.reason

    print(f"--- Workflow Transition: Supervisor → {goto.upper()} ---")

    return Command(
        update={
            "messages": [
                HumanMessage(content=reason, name="supervisor")
            ]
        },
        goto=goto,
    )

def enhancer_node(state: MessagesState) -> Command[Literal["supervisor"]]:

    """
        Enhancer agent node that improves and clarifies user queries.
        Takes the original user input and transforms it into a more precise,
        actionable request before passing it to the supervisor.
    """

    system_prompt = (
        "You are a Query Refinement Specialist with expertise in transforming vague requests into precise instructions. Your responsibilities include:\n\n"
        "1. Analyzing the original query to identify key intent and requirements\n"
        "2. Resolving any ambiguities without requesting additional user input\n"
        "3. Expanding underdeveloped aspects of the query with reasonable assumptions\n"
        "4. Restructuring the query for clarity and actionability\n"
        "5. Ensuring all technical terminology is properly defined in context\n\n"
        "Important: Never ask questions back to the user. Instead, make informed assumptions and create the most comprehensive version of their request possible."
    )

    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]

    enhanced_query = llm.invoke(messages)

    print(f"--- Workflow Transition: Prompt Enhancer → Supervisor ---")

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=enhanced_query.content,
                    name="enhancer"
                )
            ]
        },
        goto="supervisor",
    )


def research_node(state: MessagesState) -> Command[Literal["validator"]]:

    """
        Research agent node that gathers information using Tavily search.
        Takes the current task state, performs relevant research,
        and returns findings for validation.
    """

    promt = """You are an Information Specialist with expertise in comprehensive research. Your responsibilities include:\n\n
            -1. Identifying key information needs based on the query context\n
            -2. Gathering relevant, accurate, and up-to-date information from reliable sources\n
            -3. Organizing findings in a structured, easily digestible format\n
            -4. Citing sources when possible to establish credibility\n
            -5. Focusing exclusively on information gathering - avoid analysis or implementation\n\n
            -Provide thorough, factual responses without speculation where information is unavailable."""
    research_agent = create_react_agent(
        llm,
        tools=[tavily_search],
        prompt=promt
          
    )

    result = research_agent.invoke(state)

    print(f"--- Workflow Transition: Researcher → Validator ---")

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=result["messages"][-1].content,
                    name="researcher"
                )
            ]
        },
        goto="validator",
    )


def code_node(state: MessagesState) -> Command[Literal["validator"]]:

    code_agent = create_react_agent(
        llm,
        tools=[python_repl_tool],
        state_modifier=(
            "You are a coder and analyst. Focus on mathematical calculations, analyzing, solving math questions, "
            "and executing code. Handle technical problem-solving and data tasks."
        )
    )

    result = code_agent.invoke(state)

    print(f"--- Workflow Transition: Coder → Validator ---")

    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="coder")
            ]
        },
        goto="validator",
    )


# System prompt providing clear instructions to the validator agent
system_prompt = '''
    Your task is to ensure reasonable quality.
    Specifically, you must:
    - Review the user's question (the first message in the workflow).
    - Review the answer (the last message in the workflow).
    - If the answer addresses the core intent of the question, even if not perfectly, signal to end the workflow with 'FINISH'.
    - Only route back to the supervisor if the answer is completely off-topic, harmful, or fundamentally misunderstands the question.

    - Accept answers that are "good enough" rather than perfect
    - Prioritize workflow completion over perfect responses
    - Give benefit of doubt to borderline answers

    Routing Guidelines:
    1. 'supervisor' Agent: ONLY for responses that are completely incorrect or off-topic.
    2. Respond with 'FINISH' in all other cases to end the workflow.
'''

class Validator(BaseModel):
    next: Literal["supervisor", "FINISH"] = Field(
        description="Specifies the next worker in the pipeline: 'supervisor' to continue or 'FINISH' to terminate."
    )
    reason: str = Field(
        description="The reason for the decision."
    )

def validator_node(state: MessagesState) -> Command[Literal["supervisor", "__end__"]]:

    user_question = state["messages"][0].content
    agent_answer = state["messages"][-1].content

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": agent_answer},
    ]

    response = llm.with_structured_output(Validator).invoke(messages)

    goto = response.next
    reason = response.reason

    if goto == "FINISH" or goto == END:
        goto = END
        print(" --- Transitioning to END ---")
    else:
        print(f"--- Workflow Transition: Validator → Supervisor ---")


    return Command(
        update={
            "messages": [
                HumanMessage(content=reason, name="validator")
            ]
        },
        goto=goto,
    )

graph = StateGraph(MessagesState)

graph.add_node("supervisor", supervisor_node)
graph.add_node("enhancer", enhancer_node)
graph.add_node("researcher", research_node)
graph.add_node("coder", code_node)
graph.add_node("validator", validator_node)

graph.add_edge(START, "supervisor")
app = graph.compile()


display(Image(app.get_graph(xray=True).draw_mermaid_png()))

import pprint

inputs = {
    "messages": [
        ("user", "Weather in Chennai"),
    ]
}

# for event in app.stream(inputs):
#     for key, value in event.items():
#         if value is None:
#             continue
#         last_message = value.get("messages", [])[-1] if "messages" in value else None
#         if last_message:
#             pprint.pprint(f"Output from node '{key}':")
#             pprint.pprint(last_message, indent=2, width=80, depth=None)
#             print()


# ############## answer ###################

# # --- Workflow Transition: Supervisor → RESEARCHER ---
# # "Output from node 'supervisor':"
# # HumanMessage(content='The user has requested information about the weather in Chennai, which requires collecting current data. This task is best handled by the Researcher, who can gather updated weather information for Chennai, including temperature, humidity, and other relevant weather conditions.', additional_kwargs={}, response_metadata={}, name='supervisor', id='065305be-5bd8-419a-b53b-bebca2f9ca66')

# # --- Workflow Transition: Researcher → Validator ---
# # "Output from node 'researcher':"
# # HumanMessage(content='The current weather in Chennai is as follows:\n\n- **Temperature**: 34.2°C (93.6°F)\n- **Condition**: Partly cloudy\n- **Wind Speed**: 13.6 mph (22.0 kph) from the northeast\n- **Humidity**: 56%\n- **Pressure**: 1008.0 mb (29.77 in)\n- **Visibility**: 6 kilometers (3 miles)\n- **UV Index**: 9.6\n- **Feels Like**: 42.4°C (108.4°F)\n\nAdditional temperatures today range from a minimum of around 27°C to a maximum of approximately 32°C.\n\nFor more details, you can check the weather updates from sources such as [India Today](https://www.indiatoday.in/weather/chennai-weather-forecast-today) and weather services like [WeatherAPI](https://www.weatherapi.com/).', additional_kwargs={}, response_metadata={}, name='researcher', id='89c0f335-4e99-4743-867c-2735d4ffba30')

# #  --- Transitioning to END ---
# # "Output from node 'validator':"
# # HumanMessage(content="The answer provides a detailed current weather report for Chennai, addressing the user's query about the weather. It includes temperature, condition, wind speed, humidity, pressure, visibility, UV index, and feels-like temperature. The response is sufficient for the user's general question about the weather in Chennai.", additional_kwargs={}, response_metadata={}, name='validator', id='a16c08e5-54a9-4c27-a557-4b66341638be')

# import pprint

# inputs = {
#     "messages": [
#         ("user", "Give me the 20th fibonacci number"),
#     ]
# }
# for event in app.stream(inputs):
#     for key, value in event.items():
#         if value is None:
#             continue
#         pprint.pprint(f"Output from node '{key}':")
#         pprint.pprint(value, indent=2, width=80, depth=None)
#         print()

# ############# Answer ##############
# # --- Workflow Transition: Supervisor → CODER ---
# # "Output from node 'supervisor':"
# # { 'messages': [ HumanMessage(content='The user is requesting a specific numerical result from a well-defined sequence, the Fibonacci sequence, which is best served by calculating the value using a coding implementation. The problem is clear and structured, making it appropriate to move directly to the Coder for computation.', additional_kwargs={}, response_metadata={}, name='supervisor', id='87be29a9-57af-4c6d-b5c1-a8247818b65b')]}

# # --- Workflow Transition: Coder → Validator ---
# # "Output from node 'coder':"
# # { 'messages': [ HumanMessage(content='The 20th Fibonacci number is 6765.', additional_kwargs={}, response_metadata={}, name='coder', id='dfedec00-14f1-413e-9ee3-72257b362f5d')]}

# #  --- Transitioning to END ---
# # "Output from node 'validator':"
# # { 'messages': [ HumanMessage(content="The answer correctly identifies the 20th Fibonacci number, addressing the user's request.", additional_kwargs={}, response_metadata={}, name='validator', id='fdd556cd-0b42-41a6-83b4-7ee4e3663e2e')]}