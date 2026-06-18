from dotenv import load_dotenv
from langchain_community.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
import wikipedia

load_dotenv()


system_prompt = """
You are a helpful assistant that can provide information about the weather and 
search Wikipedia for information. You have access to the following tools:"""


@tool
def get_weather(city: str) -> str:
    """Get the current weather in a city."""
    return f"The current weather in {city} is sunny with a temperature of 25°C."


@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for a query."""
    print(f"Searching Wikipedia for: {query}")
    wikipedia.set_lang("en")
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Your query is ambiguous. Here are some options: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No page found for your query."


llm = ChatOpenAI(model="gpt-4o", temperature=0.7)


agent = create_agent(
    model=llm, tools=[get_weather, wikipedia_search], system_prompt=system_prompt
)


response1 = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What you know about Lech Wales on wikipedia ? ",
            }
        ]
    }
)
print(response1)
print(response1["messages"][-1].content)
