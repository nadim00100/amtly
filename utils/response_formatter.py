import re
from typing import Dict, List, Optional, Union
from datetime import datetime


class ResponseFormatter:
    """Utility class for formatting API responses and UI content"""

    @staticmethod
    def format_chat_response(content: str, sources: List[str] = None,
                             response_type: str = "chat") -> Dict:
        """Format chat response with metadata"""

        formatted_content = ResponseFormatter._clean_response_text(content)

        # Add sources if available
        if sources:
            source_text = f"\n\n📖 **Sources:** {', '.join(sources)}"
            formatted_content += source_text

        # Add appropriate emoji prefix based on type
        emoji_prefixes = {
            'chat': '',
            'document': '📄 ',
            'form': '📝 ',
            'email': '✉️ ',
            'translation': '🌐 ',
            'error': '❌ '
        }

        prefix = emoji_prefixes.get(response_type, '')
        if prefix and not formatted_content.startswith(prefix):
            formatted_content = prefix + formatted_content

        return {
            'response': formatted_content,
            'type': response_type,
            'sources': sources or [],
            'timestamp': datetime.now().isoformat(),
            'length': len(formatted_content)
        }

    @staticmethod
    def format_error_response(error_message: str, error_code: str = None) -> Dict:
        """Format error responses consistently"""

        # Make error messages more user-friendly
        friendly_errors = {
            'file_too_large': 'File is too large. Please use files smaller than 16MB.',
            'invalid_format': 'Invalid file format. Please use PDF, PNG, JPG, or JPEG files.',
            'ocr_failed': 'Could not extract text from this file. Please ensure the image is clear.',
            'api_error': 'I encountered a temporary issue. Please try again.',
            'rate_limit': 'Too many requests. Please wait a moment and try again.',
            'validation_error': 'Please check your input and try again.',
        }

        user_friendly_message = friendly_errors.get(error_code, error_message)

        return {
            'error': user_friendly_message,
            'error_code': error_code,
            'timestamp': datetime.now().isoformat(),
            'type': 'error'
        }


    @staticmethod
    def _clean_response_text(text: str) -> str:
        """Clean and normalize response text"""
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)

        # Fix common formatting issues
        text = text.replace('**', '**')  # Normalize bold formatting
        text = text.replace('- ', '• ')  # Use bullet points

        return text.strip()

# Create global instance
response_formatter = ResponseFormatter()