import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.tools import tool
from langchain_openai import ChatOpenAI
from eodhd import APIClient
from langgraph.checkpoint.sqlite import SqliteSaver
from tavily import TavilyClient

load_dotenv()


model = ChatOpenAI(model="gpt-4o", temperature=0.7)


@tool
def get_news_stock(ticker: str) -> str:
    """Get the current news for a stock ticker."""
    api = APIClient("demo")
    try:
        resp = api.financial_news(ticker)
        return resp
    except Exception as e:
        return f"Error fetching stock news: {e.message}"


@tool
def get_live_stock_price(ticker: str) -> str:
    """Get the current stock price for a ticker."""
    api = APIClient("demo")

    try:
        resp = api.get_live_stock_prices("AAPL.US")
        return resp
    except Exception as e:
        return f"Error fetching stock price: {e.message}"


@tool
def get_tavily_information_search_web(company: str) -> str:
    """Get the tavily information for a stock company.
    This will search the web for the latest information about the company and return a summary of the findings.
    """
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    return tavily_client.search(company)


system_prompt = """You are a helpful assistant that can provide information about the current stock price for a given ticker. 
    You have access to the following tool: get_live_stock_price(ticker:str)->str: Get the current stock price for a ticker. 
    and give recommendation about the stock based on the news of the stock."""

with SqliteSaver.from_conn_string("checkpoints.db") as saver:
    saver.setup()
    agent = create_agent(
        model,
        tools=[get_live_stock_price, get_news_stock, get_tavily_information_search_web],
        system_prompt=system_prompt,
        checkpointer=saver,
    )
    while True:
        user_input = input("Enter a stock ticker (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        response = agent.invoke(
            {"messages": [{"role": "user", "content": f"{user_input}"}]},
            {"configurable": {"thread_id": "stock_price_thread"}},
        )
        print(response["messages"][-1].content)
