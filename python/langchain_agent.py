"""LangChain Agent with VecTrade Tools — Multi-agent stock research."""

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import VecTradeToolkit

# Note: Requires langchain-community with VecTrade integration
# pip install langchain langchain-openai langchain-community vectrade


def main():
    # Initialize VecTrade tools for LangChain
    toolkit = VecTradeToolkit()  # reads VECTRADE_API_KEY from env
    tools = toolkit.get_tools()

    print(f"Available tools: {[t.name for t in tools]}\n")

    # Create a financial analyst agent
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior financial analyst with access to real-time market data.
        Use the VecTrade tools to research stocks and provide data-driven analysis.
        Always cite specific numbers from the tools."""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Run analysis
    result = executor.invoke({
        "input": "Compare NVDA vs AMD: which is better positioned for AI growth in 2025? "
                 "Look at revenue growth, PE ratios, and recent price action."
    })

    print("\n=== Final Analysis ===\n")
    print(result["output"])


if __name__ == "__main__":
    main()
