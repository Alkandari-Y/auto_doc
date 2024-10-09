import os
from typing import List, TypedDict

from openai import OpenAI

Prompt = TypedDict(
    "Prompt",
    {
        "role": str,
        "content": str,
    },
)


class AiClient:

    def __init__(self, prompt: Prompt, model="gpt-3.5-turbo") -> None:
        self._prompt: Prompt = prompt
        self._model = model
        self._messages: List[Prompt] = [prompt]
        self._client = self._create_client()

    def _create_client(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        return client

    def _get_ai_response(self, messages: List[Prompt]):
        response = self._client.chat.completions.create(
            messages=messages,
            model=self._model,
        )
        return response

    def update_history(self, message: str, role="user") -> None:
        self._messages.append({"role": role, "content": message})

    def single_response(self, message: str) -> str:
        response = self._get_ai_response(
            messages=[self._prompt, {"role": "user", "content": message}],
        )
        return response.choices[0].message.content.strip()
