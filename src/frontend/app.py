import gradio as gr
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import GoogleSearchAPIWrapper, PythonREPL

from src.backend.azure_endpoint_predictor import AzureLLMEndpoint

search = DuckDuckGoSearchRun()
google_search = GoogleSearchAPIWrapper()
python_repl = PythonREPL()


python_tool = Tool(
    name="python repl",
    func=python_repl.run,
    description="useful for when you need to use python to answer a question. You should input python code",
)

duckduckgo_tool = Tool(
    name="DuckDuckGo Search",
    func=search.run,
    description="Useful for when you need to do a search on the internet to find information that another tool can't find. be specific with your input.",
)

google_tool = Tool(
    name="Google Search",
    func=search.run,
    description="Useful for when you need to do a search on the Google to find the most accurate information from the internet that another tool can't find. be specific with your input.",
)

tools = [python_tool, duckduckgo_tool, google_tool]


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
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    memory=memory,
    max_iterations=3,
    handle_parsing_errors=True,
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
