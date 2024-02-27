import json
import os
import ssl
import time
import urllib
import urllib.request
from sys import argv

import gradio as gr

assert len(argv) == 3, "Usage: python app.py <API_URL> <API_KEY>"
LLM_ENDPOINT = argv[1]
API_KEY = argv[2]

system_prompt = "You are a useful AI Assistant"


def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if (
        allowed
        and not os.environ.get("PYTHONHTTPSVERIFY", "")
        and getattr(ssl, "_create_unverified_context", None)
    ):
        ssl._create_default_https_context = ssl._create_unverified_context


allowSelfSignedHttps(
    True
)  # this line is needed if you use self-signed certificate in your scoring service.


def llm_endpoint_predict(prompt: str):
    # Request data goes here
    # The example below assumes JSON formatting which may be updated
    # depending on the format your endpoint expects.
    # More information can be found here:
    # https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
    data = {
        "input_data": {
            "input_string": [
                # {"role": "system", "content": f"{system_prompt}"},
                {"role": "user", "content": f"{prompt}"},
                {"role": "assistant", "content": ""},
            ],
            "parameters": {"k1": "v1", "k2": "v2"},
        }
    }

    body = str.encode(json.dumps(data))

    # Replace this with the primary/secondary key or AMLToken for the endpoint

    if not API_KEY:
        raise Exception("A key should be provided to invoke the endpoint")

    # The azureml-model-deployment header will force the request to go to a specific deployment.
    # Remove this header to have the request observe the endpoint traffic rules
    headers = {
        "Content-Type": "application/json",
        "Authorization": ("Bearer " + API_KEY),
        "azureml-model-deployment": "mistralai-mistral-7b-instruct",
    }

    req = urllib.request.Request(LLM_ENDPOINT, body, headers)

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        print(result)
        result = json.loads(result)["output"]
        return result
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", "ignore"))


def respond(message, chat_history):
    bot_message = llm_endpoint_predict(message)
    chat_history.append((message, bot_message))
    time.sleep(2)
    return "", chat_history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    msg.submit(respond, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8000)
