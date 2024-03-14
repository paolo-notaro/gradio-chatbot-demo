from typing import Any,List, Optional

import json
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
import os
import urllib
import urllib.request

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access your API key
API_KEY = os.getenv("API_KEY")
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT")

class AzureLLMEndpoint(LLM):
    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        

        data = {
        "input_data": {
            "input_string": [
                # {"role": "system", "content": f"{system_prompt}"},
                {"role": "user", "content": f"{prompt}"},
                {"role": "assistant", "content": ""},
            ],
            "parameters": {"max_tokens": 512}
            
            }
        }

        body = str.encode(json.dumps(data))
        print(body)

        if not API_KEY:
            raise Exception("A key should be provided to invoke the endpoint")

        # The azureml-model-deployment header will force the request to go to a specific deployment.
        # Remove this header to have the request observe the endpoint traffic rules
        headers = {
            "Content-Type": "application/json",
            "Authorization": ("Bearer " + API_KEY),
            # "azureml-model-deployment": "mistralai-mistral-7b-instruct",
        }

        req = urllib.request.Request(LLM_ENDPOINT, body, headers)

        try:
            response = urllib.request.urlopen(req)

            result = response.read()
            result = json.loads(result)["output"]
            return result
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
            print(error.info())
            print(error.read().decode("utf8", "ignore"))
            return ""
       


# llm = AzureLLMEndpoint()
# print(llm("Explain the history of india in more than 700 words."))
