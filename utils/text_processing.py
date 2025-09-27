import re
from pathlib import Path


class TextProcessor:
    def __init__(self):
        pass

    def clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep German umlauts
        text = re.sub(r'[^\w\säöüÄÖÜß\-\.\,\!\?\:\;\(\)\/]', ' ', text)

        # Normalize paragraph breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)

        return text.strip()

    def extract_sections(self, text):
        """Extract sections from German bureaucratic documents"""
        sections = []

        # Look for common section patterns
        section_patterns = [
            r'(?:^|\n)([A-Z]\.?\s+[^\n]+)',  # A. Section Title
            r'(?:^|\n)(\d+\.?\s+[^\n]+)',  # 1. Numbered sections
            r'(?:^|\n)(§\s*\d+[^\n]+)',  # § 12 Legal sections
        ]

        current_section = ""
        current_title = "Allgemeine Informationen"

        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this line is a section header
            is_header = False
            for pattern in section_patterns:
                if re.match(pattern, line):
                    # Save previous section
                    if current_section:
                        sections.append({
                            'title': current_title,
                            'content': current_section.strip()
                        })

                    # Start new section
                    current_title = line
                    current_section = ""
                    is_header = True
                    break

            if not is_header:
                current_section += line + " "

        # Add final section
        if current_section:
            sections.append({
                'title': current_title,
                'content': current_section.strip()
            })

        return sections if sections else [{'title': 'Document Content', 'content': text}]


# Create global instance
text_processor = TextProcessor()