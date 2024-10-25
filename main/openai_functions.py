import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()


class ChatGPT:
    temperature = 0
    max_tokens = 1000
    top_p = 1
    frequency_penalty = 0
    presence_penalty = 0.6
    model = "gpt-4o-mini"
    
    
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise Exception(
                "Please set OPENAI_API_KEY environment variable."
                "You can obtain API key from https://platform.openai.com/account/api-keys"
            )
        openai.api_key = api_key
    @property
    def _default_params(self):
        
        return {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "model": self.model,
        }

    def translator(self, message,translation_prompt):
        client = openai.OpenAI()
        params = {
            **self._default_params,
            "messages": [
                {
                    "role": "system",
                    "content":translation_prompt,
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
        }
        try:
            response = client.chat.completions.create(**params)
            return response.choices[0].message.content
        except Exception as E:
            print('Error from OpenAI while translating: ', E)
            return None 
    
    def scoring(self, message,scoring_prompt):
        client = openai.OpenAI()
        params = {
            **self._default_params,
            "messages": [
                {
                    "role": "system",
                    "content": scoring_prompt,
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
        }
        try:
            response = client.chat.completions.create(**params)
            # return response
            return response.choices[0].message.content
        except Exception as e:
            print('Error from OpenAI while scoring: ',e)
            return '-1'
    
