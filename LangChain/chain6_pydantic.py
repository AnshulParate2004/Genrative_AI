from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# -----------------------------
# Define Pydantic Schema
# -----------------------------
class MovieAnalysis(BaseModel):
    strengths: str = Field(description="Strengths of the movie")
    weaknesses: str = Field(description="Weaknesses of the movie")

# -----------------------------
# Initialize Model
# -----------------------------
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# -----------------------------
# Define Prompt Template
# -----------------------------
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a movie critic."),
        ("human",
         "Analyze the movie '{movie_name}' and return a JSON with keys: strengths, weaknesses.\n"
         "{format_instructions}"
        ),
    ]
)

# Pydantic parser
parser = PydanticOutputParser(pydantic_object=MovieAnalysis)

# Fill in format instructions
prompt_template = prompt_template.partial(format_instructions=parser.get_format_instructions())

# -----------------------------
# Run the chain
# -----------------------------
movie_name = "Inception"
prompt = prompt_template.format_prompt(movie_name=movie_name)

# Invoke the model and parse output
result = parser.parse(model.invoke(prompt).content)

# -----------------------------
# Print structured output
# -----------------------------
print(result)
