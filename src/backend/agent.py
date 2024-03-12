from langchain.agents import AgentType, initialize_agent
from azure_endpoint_predictor import AzureLLMEndpoint
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.tools import DuckDuckGoSearchRun, Tool
from langchain.utilities import PythonREPL, WikipediaAPIWrapper

wikipedia = WikipediaAPIWrapper()
search = DuckDuckGoSearchRun()
python_repl = PythonREPL()


python_tool = Tool(
    name="python repl",
    func=python_repl.run,
    description="useful for when you need to use python to answer a question. You should input python code",
)

wikipedia_tool = Tool(
    name="wikipedia",
    func=wikipedia.run,
    description="Useful for when you need to look up a topic, country or person on wikipedia",
)

duckduckgo_tool = Tool(
    name="DuckDuckGo Search",
    func=search.run,
    description="Useful for when you need to do a search on the internet to find information that another tool can't find. be specific with your input.",
)

tools = [python_tool, wikipedia_tool, duckduckgo_tool]


# Replace this LLM with API Endpoint class
llm = AzureLLMEndpoint()

# Prompt
prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "You are a nice chatbot having a conversation with a human."
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
)


memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
conversational_agent = initialize_agent(
    tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory
)


# Logic (backend)
def predict(user_input, history):
    input_structure = {"input": user_input}  # Assuming the chain expects this structure
    response = conversational_agent.run(input_structure)
    return response



