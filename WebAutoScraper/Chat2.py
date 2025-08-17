from groq import Groq
import json
import requests
import os
from dotenv import load_dotenv
from WebSearch import combined_search

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Example Tool: Database query placeholder
def query_db(sql):
    pass

# # Tool: Run a shell command
def run_command(command):
    import subprocess
    try:
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Command failed with error:\n{e.output}"

# Tool: Get weather from wttr.in
def get_weather(city: str):
    print("🔨 Tool called: get_weather", city)
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    return "Something went wrong"

# Tool : compiled websearch
def compiled_websearch(query: str) -> str:
    results = combined_search(query)
    return results.get("answer")

# List of tools
available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as an input and return the current weather for the city"
    },
    "compiled_websearch": {
        "fn": compiled_websearch,
        "description":"Gives infomation that you ask"
    },
    "run_command": {
        "fn": run_command,
        "description": "Execute a command in the terminal"
    }
}

# System prompt
system_prompt = """
You are a helpful AI Assistant specialized in resolving user queries.
You follow a step-by-step approach involving: start, plan, action, and observe modes.

For each user query:
- Analyze the query carefully.
- Based on the planning, select the appropriate tool from the available options.
- Execute the step using the chosen tool.
- Observe the outcome.
- Based on the observation, decide the next step and continue until the query is resolved.

Rules:
- Always follow the output JSON format.
- Proceed one step at a time and wait for the next input before continuing.
- Carefully analyze each user query before taking action.

Output JSON Format:
{
  "step": "string",
  "content": "string",
  "function": "The name of the function if the step is an action",
  "input": "Input parameter for the function"
}

Available Tools:
- compiled_websearch : Gives infomation that you ask
- get_weather : Takes a city name as an input and return the current weather for the city
- run_command : Execute a command in the terminal

Example:
User Query: What is the weather of New York?
Output: { "step": "plan", "content": "The user is interested in the weather data for New York." }
Output: { "step": "plan", "content": "From the available tools, I should call the get_weather function." }
Output: { "step": "action", "function": "get_weather", "input": "New York" }
Output: { "step": "observe", "output": "12°C" }
Output: { "step": "output", "content": "The weather in New York is approximately 12°C." }
"""

# Initialize chat history
messages = [{"role": "system", "content": system_prompt}]

print("Welcome to Groq AI! Type your questions below (Ctrl+C to exit).")

while True:
    user_query = input("> ")
    messages.append({"role": "user", "content": user_query})

    while True:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # Groq's fast LLaMA model
            response_format={"type": "json_object"},
            messages=messages,
            max_tokens=700,
            temperature=0.4
        )

        parsed_output = json.loads(completion.choices[0].message.content)
        messages.append({"role": "assistant", "content": json.dumps(parsed_output)})

        # Step: Plan
        if parsed_output.get("step") == "plan":
            print(f"🧠: {parsed_output.get('content')}")
            continue

        # Step: Action
        if parsed_output.get("step") == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")
            if tool_name in available_tools:
                output = available_tools[tool_name]["fn"](tool_input)
                messages.append({"role": "assistant", "content": json.dumps({"step": "observe", "output": output})})
                continue

        # Step: Output
        if parsed_output.get("step") == "output":
            print(f"🤖: {parsed_output.get('content')}")
            break

        
