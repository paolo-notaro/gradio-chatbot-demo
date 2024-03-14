
import gradio as gr
from langchain.agents import AgentType, initialize_agent
from src.backend.azure_endpoint_predictor import AzureLLMEndpoint
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.tools import DuckDuckGoSearchRun, Tool

# !pip -q install wikipedia
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
    tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory, max_iterations=3,
)


# Logic (backend)
def predict(user_input, history):
    input_structure = {"input": user_input}  # Assuming the chain expects this structure
    response = conversational_agent.run(input_structure)
    return response


markdown_title = """
    <h1>IABG-Chat - IABG's ChatGPT </h1>
    <style>
         .gradio-container-3-50-2 .prose h1 {
            text-align: center;
            margin-top : 10px;
            padding-top : 10px;
            font-size: 2em;
         }
    </style>
"""


def create_header_row() -> None:
    """creates a header row for the interface using the specified parameters."""
    with gr.Row():
        gr.Image(
            "images/iabg_logo.png",
            width=5,
            height=75,
            scale=0,
            image_mode="RGBA",
            show_label=False,
            show_download_button=False,
        )
        gr.Markdown(markdown_title)


# UI Elements (Frontend)
with gr.Blocks() as demo:
    create_header_row()
    gr.ChatInterface(predict)

# Launch the gradio app for 72 hours
demo.queue(concurrency_count=40).launch(
    # share=True,
    server_name="0.0.0.0", 
    server_port=8000,
    debug=True,
)
