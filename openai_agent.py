import json
from openai import OpenAI
from base import BaseAgent
import tiktoken


class OpenAIAgent(BaseAgent):
    def __init__(self, model_slug, api_key):
        super().__init__()
        self.client = OpenAI(api_key=api_key)
        self.model = model_slug

    def _is_chat_model(self):
        return self.model.startswith("gpt")

    def _is_embed_model(self):
        return self.model.startswith("text")

    def generate(self, user_request):
        if not self._is_chat_model():
            return None
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": user_request}],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()

    def generate_json(self, user_request, schema):
        if not self._is_chat_model():
            return None
        prompt = f"""Return ONLY valid JSON.

Schema:
{schema}

User request:
{user_request}
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        content = response.choices[0].message.content.strip()
        try:
            return json.loads(content)
        except:
            return content

    def stream(self, user_request):
        if not self._is_chat_model():
            return None
        stream = self.client.responses.create(
            model=self.model,
            input=user_request,
            stream=True
        )
        for event in stream:
            yield event

    def embed(self, query):
        if not self._is_embed_model():
            return None
        response = self.client.embeddings.create(
            input=query,
            model=self.model
        )
        return response.data[0].embedding

    def batch_generate(self, batch):
        if not self._is_chat_model():
            return []
        return [self.generate(x) for x in batch]

    def batch_embed(self, batch):
        if not self._is_embed_model():
            return []
        return [self.embed(x) for x in batch]

    def count_tokens(self, query):
        enc = tiktoken.encoding_for_model(self.model)
        return len(enc.encode(query))

    def info(self):
        return f"OpenAI Agent: {self.model}"