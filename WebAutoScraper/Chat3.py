from groq import Groq
import json
import requests
import os
from dotenv import load_dotenv
from WebSearch import combined_search
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

# ----------------------------
# Client
# ----------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ----------------------------
# Tools
# ----------------------------
def run_command(command: str):
    """Run a terminal command with a hard timeout to avoid hanging."""
    import subprocess
    command = (command or "").strip()
    if not command:
        return "No command provided."

    try:
        output = subprocess.check_output(
            command,
            shell=True,
            text=True,
            stderr=subprocess.STDOUT,
            timeout=15,  # ⏲️ hard-stop after 15s
        )
        return output.strip()
    except subprocess.TimeoutExpired:
        return "Command timed out after 15s."
    except subprocess.CalledProcessError as e:
        return f"Command failed:\n{e.output}"

def get_weather(city: str):
    """Simple weather via wttr.in."""
    city = (city or "").strip()
    if not city:
        return "Please provide a city."
    print("🔨 Tool called: get_weather", city)
    url = f"https://wttr.in/{city}?format=%C+%t"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return f"The weather in {city} is {r.text}."
        return f"Weather lookup failed with status {r.status_code}."
    except requests.RequestException as e:
        return f"Weather lookup error: {e}"

def compiled_websearch(query: str) -> str:
    """Your aggregator. Expects combined_search to return a dict with 'answer' key."""
    query = (query or "").strip()
    if not query:
        return "Please provide a query."
    results = combined_search(query)
    return results.get("answer", "No answer available.")

def get_time(place_or_tz: str) -> str:
    """
    Safe current time tool (no shell).
    Accepts either a city hint (e.g., 'India', 'Nagpur', 'Delhi') or a TZ string like 'Asia/Kolkata'.
    """
    s = (place_or_tz or "").strip().lower()
    if not s:
        return "Please provide a place or timezone."

    # Simple mappings
    if any(k in s for k in ["india", "ist", "kolkata", "delhi", "mumbai", "nagpur"]):
        tz = "Asia/Kolkata"
    elif "/" in s:  # user provided something like 'Europe/London'
        tz = place_or_tz.strip()
    else:
        # Fallback to UTC if unknown
        tz = "UTC"

    try:
        now = datetime.now(ZoneInfo(tz))
        return f"Current time in {tz} is {now.strftime('%Y-%m-%d %H:%M:%S')}."
    except Exception:
        now = datetime.utcnow()
        return f"Unknown timezone. UTC time is {now.strftime('%Y-%m-%d %H:%M:%S')}."

available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Return current weather for a city."
    },
    "compiled_websearch": {
        "fn": compiled_websearch,
        "description": "Web answers for general queries."
    },
    "run_command": {
        "fn": run_command,
        "description": "Execute a terminal command (15s timeout)."
    },
    "get_time": {
        "fn": get_time,
        "description": "Get current time by city hint or timezone."
    },
}

# ----------------------------
# System Prompt
# ----------------------------
system_prompt = """
You are a helpful AI assistant that follows a strict JSON step protocol.

For each user query:
1) Make a brief "plan".
2) Then immediately either:
   - produce an "action" (choose a tool and input), or
   - produce an "ask_user" if you truly need clarification (include a 'question').
3) After an "action", expect the system to run the tool and provide an "observe" message.
4) Based on the observation, decide the next "action" or produce the final "output".
5) Never stay in "plan" on consecutive turns. After one plan, ALWAYS move to "action" or "ask_user".
6) Never call run_command for time/date. Use get_time for that.

Valid steps and required fields:
- { "step": "plan", "content": "<short plan>" }
- { "step": "ask_user", "question": "<what you need from the user>" }
- { "step": "action", "function": "<tool name>", "input": "<string input for tool>" }
- { "step": "observe", "output": "<filled by system after tool>" }  # (model shouldn't emit this)
- { "step": "output", "content": "<final answer for the user>" }

Return ONE valid JSON object only.
Available tools: get_weather, compiled_websearch, get_time, run_command.
"""

# ----------------------------
# Chat Loop
# ----------------------------
messages = [{"role": "system", "content": system_prompt}]
print("Welcome to Groq AI! Type your questions below (Ctrl+C to exit).")

MAX_MESSAGES = 40  # keep context light

def trim_history(msgs, max_len=MAX_MESSAGES):
    if len(msgs) <= max_len:
        return msgs
    return [msgs[0]] + msgs[-(max_len-1):]  # keep system + last N-1

while True:
    user_query = input(">> ").strip()
    if not user_query:
        print("⚠️  Empty input ignored. Please enter a valid query.")
        continue

    messages.append({"role": "user", "content": user_query})
    messages = trim_history(messages)

    while True:
        try:
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                response_format={"type": "json_object"},
                messages=messages,
                max_tokens=700,
                temperature=0.4,
            )
            raw = completion.choices[0].message.content
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Nudge model to send valid JSON once
            messages.append({"role": "user", "content": "Return ONE valid JSON object matching the schema."})
            messages = trim_history(messages)
            continue

        # Log assistant JSON to history
        messages.append({"role": "assistant", "content": json.dumps(parsed)})
        messages = trim_history(messages)

        step = (parsed.get("step") or "").lower()

        if step == "plan":
            print(f"🧠: {parsed.get('content', '').strip() or 'Planning...'}")
            # Auto-advance: politely instruct model to proceed
            messages.append({"role": "user", "content": "Proceed to the next step (action or ask_user)."})
            messages = trim_history(messages)
            continue

        if step == "ask_user":
            q = (parsed.get("question") or "").strip()
            if not q:
                print("🤖: I need more information. Please clarify.")
            else:
                print(f"❓: {q}")
            answer = input("> ").strip()
            if not answer:
                print("⚠️  Empty input ignored. Please enter a valid answer.")
                continue
            messages.append({"role": "user", "content": answer})
            messages = trim_history(messages)
            continue

        if step == "action":
            tool_name = (parsed.get("function") or "").strip()
            tool_input = (parsed.get("input") or "").strip()
            if tool_name in available_tools:
                try:
                    output = available_tools[tool_name]["fn"](tool_input)
                except Exception as e:
                    output = f"Tool error: {e}"
            else:
                output = f"Unknown tool: {tool_name}"

            # Feed observation back to the model
            messages.append({"role": "assistant", "content": json.dumps({"step": "observe", "output": output})})
            messages = trim_history(messages)
            continue

        if step == "output":
            print(f"🤖: {parsed.get('content', '').strip()}")
            break

        # Fallback if step is unexpected
        print("🛑: I encountered an unexpected step from the model. Ending turn.")
        break
