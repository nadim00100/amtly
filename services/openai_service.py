from openai import OpenAI
from config import Config


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.MAX_TOKENS
        self.temperature = Config.TEMPERATURE

    def get_response(self, user_message, system_prompt=None, clean_context=True):
        """Get response from OpenAI for user message with clean context"""
        try:
            # Ensure clean message structure - no conversation history contamination
            messages = []

            # Add system prompt if provided
            if system_prompt:
                # Clean system prompt of any potential contamination
                clean_system_prompt = str(system_prompt).strip()
                messages.append({"role": "system", "content": clean_system_prompt})

            # Add user message - ensure it's clean
            clean_user_message = str(user_message).strip()
            messages.append({"role": "user", "content": clean_user_message})

            # Make API call with clean context
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract clean response
            response_content = response.choices[0].message.content.strip()

            # Additional cleanup - remove any trailing artifacts
            response_content = self._clean_response_content(response_content)

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

    def _clean_response_content(self, content):
        """Clean response content of any artifacts or contamination"""
        if not content:
            return ""

        # Remove common trailing artifacts that might appear
        lines = content.split('\n')
        cleaned_lines = []

        skip_next = False
        for i, line in enumerate(lines):
            line = line.strip()

            # Skip empty lines at the end
            if not line and i == len(lines) - 1:
                continue

            # Skip obvious AI artifacts or repeated content
            if skip_next:
                skip_next = False
                continue

            # Check for common AI artifacts
            artifacts = [
                "Of course! In order to provide",
                "could you please specify",
                "feel free to provide me with",
                "I can assist you more effectively",
                "---",
                "Is there anything else",
                "How can I help you"
            ]

            # If line starts with an artifact pattern, skip it and potentially the next line
            if any(artifact.lower() in line.lower() for artifact in artifacts):
                # Check if this seems like a trailing artifact (usually at the end)
                remaining_content = '\n'.join(lines[i + 1:]).strip()
                if len(remaining_content) < 50:  # If very little content remains, likely an artifact
                    break

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    def get_translation(self, text, source_lang, target_lang):
        """Get translation with specific prompt"""
        system_prompt = f"""You are a professional translator. Translate the following text from {source_lang} to {target_lang}.
        Provide only the translation, no additional commentary or explanations."""

        return self.get_response(f"Translate: {text}", system_prompt)

    def get_analysis(self, text, analysis_type="general"):
        """Get analysis with specific prompt"""
        system_prompt = f"""You are a document analyst. Provide a {analysis_type} analysis of the following text.
        Be concise and focus on the key points."""

        return self.get_response(f"Analyze: {text}", system_prompt)


# Create a global instance
openai_service = OpenAIService()