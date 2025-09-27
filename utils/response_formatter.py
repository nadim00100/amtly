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
    def format_document_analysis(extracted_text: str, metadata: Dict = None) -> str:
        """Format document analysis results"""
        if not extracted_text or not extracted_text.strip():
            return "I couldn't extract readable text from this document. Please ensure it's clear and well-scanned."

        # Clean and truncate if necessary
        cleaned_text = ResponseFormatter._clean_response_text(extracted_text)

        # Add metadata if available
        if metadata:
            doc_info = []
            if metadata.get('pages'):
                doc_info.append(f"{metadata['pages']} pages")
            if metadata.get('language'):
                doc_info.append(f"Language: {metadata['language']}")
            if metadata.get('confidence'):
                doc_info.append(f"Confidence: {metadata['confidence']:.1%}")

            if doc_info:
                info_text = f"\n\n📊 **Document Info:** {', '.join(doc_info)}"
                cleaned_text += info_text

        return cleaned_text

    @staticmethod
    def format_form_explanation(form_data: Dict, explanation_type: str = "overview") -> str:
        """Format form explanations"""

        if explanation_type == "overview":
            return ResponseFormatter._format_form_overview(form_data)
        elif explanation_type == "field":
            return ResponseFormatter._format_field_explanation(form_data)
        elif explanation_type == "section":
            return ResponseFormatter._format_section_explanation(form_data)

        return "Form explanation not available."

    @staticmethod
    def format_translation_result(original_text: str, translated_text: str,
                                  source_lang: str, target_lang: str) -> str:
        """Format translation results"""

        lang_names = {
            'de': 'German',
            'en': 'English',
            'ar': 'Arabic'
        }

        source_name = lang_names.get(source_lang, source_lang.upper())
        target_name = lang_names.get(target_lang, target_lang.upper())

        formatted_result = f"**Translation ({source_name} → {target_name}):**\n\n"
        formatted_result += ResponseFormatter._clean_response_text(translated_text)

        # Add length info if significant difference
        original_length = len(original_text.split())
        translated_length = len(translated_text.split())

        if abs(original_length - translated_length) > original_length * 0.3:
            formatted_result += f"\n\n💡 **Note:** Translation length differs significantly from original ({original_length} → {translated_length} words)."

        return formatted_result

    @staticmethod
    def format_email_template(email_content: str, email_type: str) -> str:
        """Format generated email templates"""

        # Ensure proper email structure
        if not email_content.startswith('Betreff:') and not email_content.startswith('Subject:'):
            email_content = f"Betreff: {email_type}\n\n{email_content}"

        # Add copy instruction
        copy_instruction = "\n\n💡 **Tip:** You can copy this email and customize it with your personal details."

        return email_content + copy_instruction

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

    @staticmethod
    def _format_form_overview(form_data: Dict) -> str:
        """Format form overview"""
        form_name = form_data.get('name', 'Unknown Form')
        description = form_data.get('description', 'No description available')

        formatted = f"**{form_name}**\n\n{description}\n\n"

        sections = form_data.get('sections', [])
        if sections:
            formatted += "**Main Sections:**\n"
            for section in sections:
                formatted += f"• {section.get('title', 'Untitled Section')}\n"

        return formatted

    @staticmethod
    def _format_field_explanation(field_data: Dict) -> str:
        """Format individual field explanation"""
        label = field_data.get('label', 'Unknown Field')
        helper = field_data.get('helper', '')
        example = field_data.get('example', '')

        formatted = f"**{label}**\n\n"

        if helper:
            formatted += f"{helper}\n\n"

        if example:
            formatted += f"**Example:** {example}\n\n"

        if field_data.get('required'):
            formatted += "⚠️ **This field is required**"

        return formatted

    @staticmethod
    def _format_section_explanation(section_data: Dict) -> str:
        """Format section explanation"""
        title = section_data.get('title', 'Unknown Section')
        fields = section_data.get('fields', [])

        formatted = f"**{title}**\n\n"

        if fields:
            formatted += "**Fields in this section:**\n"
            for field in fields:
                required_mark = " **(Required)**" if field.get('required') else ""
                formatted += f"• {field.get('label', 'Untitled Field')}{required_mark}\n"

        return formatted

    @staticmethod
    def format_knowledge_base_response(content: str, search_results: List[Dict]) -> str:
        """Format responses that use knowledge base search"""

        formatted_content = ResponseFormatter._clean_response_text(content)

        # Add confidence indicator based on search results
        if search_results:
            avg_score = sum(result.get('score', 0) for result in search_results) / len(search_results)

            if avg_score > 0.8:
                confidence = "High confidence - found exact matches"
            elif avg_score > 0.6:
                confidence = "Medium confidence - found related information"
            else:
                confidence = "Low confidence - limited relevant information found"

            formatted_content += f"\n\n🔍 **Search Quality:** {confidence}"

        return formatted_content


# Create global instance
response_formatter = ResponseFormatter()