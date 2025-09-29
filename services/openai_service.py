from openai import OpenAI
from config import Config


class OpenAIService:
    """OpenAI service - CLEANED & SIMPLIFIED VERSION"""

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.MAX_TOKENS
        self.temperature = Config.TEMPERATURE

    def get_response(self, user_message, system_prompt=None, clean_context=True):
        """Get response from OpenAI with clean context"""
        try:
            messages = []

            # Add system prompt if provided
            if system_prompt:
                clean_system_prompt = str(system_prompt).strip()
                messages.append({"role": "system", "content": clean_system_prompt})

            # Add user message
            clean_user_message = str(user_message).strip()
            messages.append({"role": "user", "content": clean_user_message})

            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract response
            response_content = response.choices[0].message.content.strip()

            return {
                "success": True,
                "response": response_content,
                "usage": response.usage
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "Sorry, I encountered an error. Please try again."
            }


# Create global instance
openai_service = OpenAIService()