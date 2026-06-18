from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.tools import tool
from langchain_openai import ChatOpenAI
from eodhd import APIClient
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

system_prompt = """You are a helpful assistant that can provide information about the 
current stock price for a given ticker. You have access to the following tool:
get_live_stock_price(ticker:str)->str: Get the current stock price for a ticker. and give recommendation about the stock based on the news of the stock."""


@tool
def get_news_stock(ticker: str) -> str:
    """Get the current news for a stock ticker."""
    api = APIClient("demo")
    try:
        resp = api.financial_news(ticker)
        return str(resp)
    except Exception as e:
        return f"Error fetching stock news: {str(e)}"


@tool
def get_live_stock_price(ticker: str) -> str:
    """Get the current stock price for a ticker."""
    api = APIClient("demo")

    try:
        resp = api.get_live_stock_prices("AAPL.US")
        return str(resp)
    except Exception as e:
        return f"Error fetching stock price: {str(e)}"


agent = create_agent(
    llm,
    tools=[get_live_stock_price, get_news_stock],
    system_prompt=system_prompt,
    checkpointer=InMemorySaver(),
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