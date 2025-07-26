from openai import OpenAI
import json 
import requests
import os
from dotenv import load_dotenv

load_dotenv() 

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY") 
    )


def query_db(sql):
    pass

def run_command(command):
    import subprocess
    try:
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Command failed with error:\n{e.output}"


def get_weather(city:str):
    # do atually api call 
    print("🔨 Tool called: get_weather",city)
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    return "Something went wrong"
available_tools = {
    "get_weather":{
        "fn": get_weather,
        "description": "Takes a city name as an input and return the current weather for the city "
    },
    "run_command":{
        "fn": run_command,
        "description": "Execute a command in the terminal "
    }
}

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
{{
  "step": "string",
  "content": "string",
  "function": "The name of the function if the step is an action"
  "input":"Input parameter for the function"
}}

Available Tools:
- get_weather: Takes a city name as an input and return the current weather for the city
- run_command: Execute a command in the terminal

Example:
User Query: What is the whether of new york?
Output: {{ "step": "plan", "content": "The user is interested in the weather data for New York." }}
Output: {{ "step": "plan", "content": "From the available tools, I should call the get_weather function." }}
Output: {{ "step": "action", "function": "get_weather", "input": "New York" }}
Output: {{ "step": "observe", "output": "12°C" }}
Output: {{ "step": "output", "content": "The weather in New York is approximately 12°C." }}


"""

messages = [
            {"role":"system", "content": system_prompt}
        ]
while True:
    user_query = input('> ') 
    messages.append({"role": "user", "content": user_query})

    while True:
        completion = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            response_format= {"type":"json_object"},
            messages=messages,
            max_tokens=1000,
            temperature=0.4
        )
        parsed_output = json.loads(completion.choices[0].message.content)
        messages.append({"role":"assistant","content": json.dumps(parsed_output)})
        
        if parsed_output.get("step") == "plan":
            print(f"🧠:{parsed_output.get('content')}")
            continue


        if parsed_output.get("step") == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")
            
            if tool_name in available_tools:
                output = available_tools[tool_name].get("fn")(tool_input)
                messages.append({"role":"assistant", "content":json.dumps({"step": "observe", "output": output})})
                continue
            
        if parsed_output.get("step") == "output":
            print(f"🤖:{parsed_output.get('content')}")
            break


"""
completion = client.chat.completions.create(
        model="gpt-4o",
        response_format= {"type":"json_object"},
        messages=[
            {"role":"system", "content":system_prompt},
            {"role":"user", "content":"What is current weather of Patiala?"},
            {"role":"assistant","content":json.dumps({ "step": "plan", "content": "The user is interested in the current weather data for Patiala." })},
            {"role":"assistant","content":json.dumps({"step": "plan", "content": "From the available tools, I should call the get_weather function to retrieve the weather information for Patiala."})},
            {"role":"assistant", "content":json.dumps({"step": "action", "function": "get_weather", "input": "Patiala"})},
            {"role":"assistant", "content":json.dumps({"step": "observe", "output": "28°C"})},
        ] ,
        max_tokens=1000,
        temperature=0.4
    )
print(completion.choices[0].message.content.strip())
"""