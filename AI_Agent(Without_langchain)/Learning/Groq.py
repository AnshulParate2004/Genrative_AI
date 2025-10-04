import os
import json
import requests
import subprocess
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable not set. Please set it in .env or environment.")

client = Groq(api_key=api_key)

# Tool: Database query placeholder
def query_db(sql):
    pass  # Placeholder, not implemented

# Tool: Run a shell command
def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Command failed with error:\n{e.output}"

# Tool: Get weather from wttr.in
def get_weather(city: str):
    print(f"🔨 Tool called: get_weather({city})")
    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise exception for bad status codes
        return f"The weather in {city} is {response.text}."
    except requests.RequestException as e:
        return f"Failed to fetch weather for {city}: {str(e)}"

# List of available tools
available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as input and returns the current weather for the city"
    },
    "run_command": {
        "fn": run_command,
        "description": "Executes a command in the terminal"
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
- get_weather: Takes a city name as input and returns the current weather for the city
- run_command: Executes a command in the terminal

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

try:
    while True:
        user_query = input("> ")
        messages.append({"role": "user", "content": user_query})

        while True:
            try:
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

            except json.JSONDecodeError as e:
                print(f"🤖: Error parsing model response: {str(e)}")
                break
            except Exception as e:
                print(f"🤖: Error during processing: {str(e)}")
                break

except KeyboardInterrupt:
    print("\nExiting Groq AI. Goodbye!")