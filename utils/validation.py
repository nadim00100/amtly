import re
from typing import Dict, List, Optional, Union
from pathlib import Path


class ValidationUtils:
    """Utility class for input validation"""

    # Common validation patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^[\+]?[1-9][\d]{0,15}$')

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
    def validate_email(email: str) -> tuple[bool, str]:
        """Validate email address format"""
        if not email or not email.strip():
            return False, "Email is required"

        email = email.strip().lower()

        if not ValidationUtils.EMAIL_PATTERN.match(email):
            return False, "Please enter a valid email address"

        return True, ""

    @staticmethod
    def validate_language_code(lang_code: str) -> tuple[bool, str]:
        """Validate language code"""
        valid_codes = ['auto', 'de', 'en', 'ar']

        if not lang_code or lang_code not in valid_codes:
            return False, f"Language must be one of: {', '.join(valid_codes)}"

        return True, ""

    @staticmethod
    def validate_form_id(form_id: str) -> tuple[bool, str]:
        """Validate form ID"""
        valid_forms = ['HA', 'VM', 'WEP', 'KDU', 'EK']

        if not form_id or form_id.upper() not in valid_forms:
            return False, f"Form ID must be one of: {', '.join(valid_forms)}"

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

    @staticmethod
    def validate_query_parameters(params: Dict) -> Dict[str, Union[bool, str]]:
        """Validate multiple query parameters"""
        results = {}

        # Validate language if present
        if 'language' in params:
            is_valid, error = ValidationUtils.validate_language_code(params['language'])
            results['language'] = {'valid': is_valid, 'error': error}

        # Validate message if present
        if 'message' in params:
            is_valid, error = ValidationUtils.validate_chat_message(params['message'])
            results['message'] = {'valid': is_valid, 'error': error}

        # Validate form_id if present
        if 'form_id' in params:
            is_valid, error = ValidationUtils.validate_form_id(params['form_id'])
            results['form_id'] = {'valid': is_valid, 'error': error}

        return results

    @staticmethod
    def is_safe_redirect_url(url: str, allowed_hosts: List[str] = None) -> bool:
        """Check if URL is safe for redirects"""
        if not url:
            return False

        # Only allow relative URLs or specific hosts
        if url.startswith('/'):
            return True

        if allowed_hosts:
            for host in allowed_hosts:
                if url.startswith(f'http://{host}') or url.startswith(f'https://{host}'):
                    return True

        return False


# Create global instance
validation_utils = ValidationUtils()