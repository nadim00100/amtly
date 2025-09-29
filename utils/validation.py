import re
from typing import Dict
from pathlib import Path


class ValidationUtils:
    """Utility class for input validation - CLEANED VERSION"""

    @staticmethod
    def validate_text_input(text: str, min_length: int = 1, max_length: int = 1000,
                            required: bool = True) -> tuple[bool, str]:
        """Validate text input with length constraints"""
        if not text or not text.strip():
            if required:
                return False, "This field is required"
            return True, ""

        text = text.strip()

        if len(text) < min_length:
            return False, f"Text must be at least {min_length} characters long"

        if len(text) > max_length:
            return False, f"Text must be no more than {max_length} characters long"

        return True, ""

    @staticmethod
    def validate_chat_message(message: str) -> tuple[bool, str]:
        """Validate chat message"""
        # Check basic text validation
        is_valid, error = ValidationUtils.validate_text_input(
            message, min_length=1, max_length=1000, required=True
        )

        if not is_valid:
            return is_valid, error

        # Check for potential malicious content
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'data:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
        ]

        message_lower = message.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, message_lower):
                return False, "Message contains potentially harmful content"

        return True, ""

    @staticmethod
    def validate_file_upload(file_info: Dict) -> tuple[bool, str]:
        """Validate uploaded file"""
        if not file_info:
            return False, "No file information provided"

        # Check file name
        filename = file_info.get('name', '')
        if not filename:
            return False, "File name is required"

        # Check file size
        file_size = file_info.get('size', 0)
        max_size = 16 * 1024 * 1024  # 16MB

        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            return False, f"File too large. Maximum size is {max_mb}MB"

        # Check file extension
        file_ext = Path(filename).suffix.lower()
        allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg'}

        if file_ext not in allowed_extensions:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"

        return True, ""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text input"""
        if not text:
            return ""

        # Remove potentially harmful characters
        text = re.sub(r'[<>"\']', '', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()


# Create global instance
validation_utils = ValidationUtils()