from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import os

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
os.environ["ABSL_CPP_MIN_LOG_LEVEL"] = "2"  # suppress Google Gemini warnings

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -----------------------------
# Messages
# -----------------------------
messages = [
    SystemMessage(content="Solve the following math problems"),
    HumanMessage(content="What is the square root of 49?"),
]

# -----------------------------
# Google Gemini 2.5 Pro
# Docs: https://ai.google.dev/gemini-api/docs
# -----------------------------
gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    api_key=GOOGLE_API_KEY
)

gemini_result = gemini.invoke(messages)

print(f"Answer from Google Gemini Pro: {gemini_result.content}")

# -----------------------------
# Groq Llama-3.3-70B
# Docs: https://console.groq.com/docs
# -----------------------------
groq = ChatGroq(
    model_name="llama-3.3-70b-versatile",  # latest supported model
    api_key=GROQ_API_KEY
)

groq_result = groq.invoke(messages)
print(f"Answer from Groq Llama-3.3-70B: {groq_result.content}")
