import openai
from core.config import get_openai_key

class LLMService:
    def __init__(self, model: str = "o3"):
        self.api_key = get_openai_key()
        if not self.api_key:
            raise RuntimeError("OpenAI API key not found.")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model

    def chat(self, messages: list) -> str:
        """Send messages to LLM and get response content."""
        response = self.client.responses.create(
            model=self.model,
            input=self._format_input(messages)
        )
        return self._extract_content(response)

    def _format_input(self, messages: list) -> str:
        # Simple formatting for now, can be improved
        return "\n".join([f"{m['role']}: {m['content']}" for m in messages])

    def _extract_content(self, response) -> str:
        for output in response.output:
            if hasattr(output, 'content'):
                return output.content[0].text
        raise ValueError(f"No content found in response: {response}")
