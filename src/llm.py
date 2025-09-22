import anthropic
import os

class LLM:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.system_prompt = """ 
        - You review stock data and create estimates based on recent.
        - Generate buy, sell, or hold recommendations for the next 30 days (including prices to buy and/or sell)
        - Be brief and concise in your recommendations
        """ 
        self.max_tokens = 5000

    def generate_response(self, prompt: str, model: str = 'claude-3-5-haiku-latest'):
        params = {
            "model": model,
            "max_tokens": self.max_tokens,
            "system": self.system_prompt,
            "messages": [{"role": "user", "content": prompt}],
        }
        response = self.client.messages.create(**params)

        return response.content[0].text


