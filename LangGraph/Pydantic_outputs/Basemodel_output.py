from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest")

class Country(BaseModel):

    """Information about a country"""

    name: str = Field(description="name of the country")
    language: str = Field(description="language of the country")
    capital: str = Field(description="Capital of the country")
 
structured_llm = llm.with_structured_output(Country)
structured_llm

pr = structured_llm.invoke("Tell me about France")
print(pr)
# Answer :Country ( name="France", language="French", capital="Paris")
  