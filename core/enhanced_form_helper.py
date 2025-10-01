"""
Enhanced Form Helper with structured knowledge base
Provides field-level guidance and form-specific assistance
"""

import re
from typing import Dict, List, Optional, Tuple
from data.form_knowledge_base import (
    FORM_SCHEMAS, FORM_TRIGGERS, COMMON_MISTAKES, REQUIRED_DOCUMENTS
)
from services.openai_service import openai_service
from services.vector_store import vector_store


class EnhancedFormHelper:
    """Form helper with structured knowledge and intelligent routing"""

    def __init__(self):
        self.form_schemas = FORM_SCHEMAS
        self.form_triggers = FORM_TRIGGERS
        self.common_mistakes = COMMON_MISTAKES
        self.required_documents = REQUIRED_DOCUMENTS

        # Form code mappings
        self.form_codes = {
            'ha': 'HA',
            'hauptantrag': 'HA',
            'vm': 'VM',
            'vermögen': 'VM',
            'vermoegen': 'VM',
            'asset': 'VM',
            'kdu': 'KDU',
            'unterkunft': 'KDU',
            'housing': 'KDU',
            'wep': 'WEP',
            'weitere person': 'WEP',
            'additional person': 'WEP',
            'wba': 'WBA',
            'weiterbewilligung': 'WBA',
            'renewal': 'WBA'
        }

    def detect_form_and_field(self, user_message: str) -> Dict:
        """
        Detect which form and optionally which field/section user is asking about

        Returns:
            {
                'form_code': 'HA' or None,
                'field': '3' or '16-17' or None,
                'section': 'A' or None,
                'confidence': 'high'/'medium'/'low'
            }
        """
        message_lower = user_message.lower()

        # Step 1: Detect form
        form_code = None
        confidence = 'low'

        for keyword, code in self.form_codes.items():
            if keyword in message_lower:
                form_code = code
                confidence = 'high'
                break

        # Step 2: Detect field number
        field = None

        # Look for patterns like "field 3", "feld 16", "question 24", "zeile 10"
        field_patterns = [
            r'field\s+(\d+)',
            r'feld\s+(\d+)',
            r'question\s+(\d+)',
            r'frage\s+(\d+)',
            r'zeile\s+(\d+)',
            r'line\s+(\d+)',
            r'number\s+(\d+)',
            r'nummer\s+(\d+)',
            r'#(\d+)',
            r'\b(\d+)\b'  # Any standalone number
        ]

        for pattern in field_patterns:
            match = re.search(pattern, message_lower)
            if match:
                field = match.group(1)
                break

        # Step 3: Detect section
        section = None
        section_patterns = [
            r'section\s+([a-h])',
            r'abschnitt\s+([a-h])',
            r'teil\s+([a-h])',
            r'part\s+([a-h])'
        ]

        for pattern in section_patterns:
            match = re.search(pattern, message_lower)
            if match:
                section = match.group(1).upper()
                break

        # Step 4: Infer form from context keywords if not explicitly mentioned
        if not form_code:
            if any(word in message_lower for word in ['bank', 'iban', 'konto', 'account']):
                form_code = 'HA'
                confidence = 'medium'
            elif any(word in message_lower for word in ['vermögen', 'asset', 'savings', 'spareinlage']):
                form_code = 'VM'
                confidence = 'medium'
            elif any(word in message_lower for word in ['miete', 'rent', 'wohnung', 'housing', 'heizung']):
                form_code = 'KDU'
                confidence = 'medium'
            elif any(word in message_lower for word in ['partner', 'spouse', 'ehepartner', 'kind', 'child']):
                form_code = 'WEP'
                confidence = 'medium'
            elif any(word in message_lower for word in ['renewal', 'weiterbewilligung', 'verlängerung', 'extend']):
                form_code = 'WBA'
                confidence = 'medium'

        return {
            'form_code': form_code,
            'field': field,
            'section': section,
            'confidence': confidence
        }

    def get_field_guidance(self, form_code: str, field: str) -> Optional[Dict]:
        """Get structured guidance for a specific field"""
        if form_code not in self.form_schemas:
            return None

        form_schema = self.form_schemas[form_code]

        # Search through sections for the field
        for section_code, section_data in form_schema.get('sections', {}).items():
            fields = section_data.get('fields', {})

            # Direct match
            if field in fields:
                return fields[field]

            # Range match (e.g., field "16" matches "16-17")
            for field_key, field_data in fields.items():
                if '-' in field_key:
                    start, end = field_key.split('-')
                    if start <= field <= end:
                        return field_data

        return None

    def get_section_guidance(self, form_code: str, section: str) -> Optional[Dict]:
        """Get guidance for an entire section"""
        if form_code not in self.form_schemas:
            return None

        form_schema = self.form_schemas[form_code]
        return form_schema.get('sections', {}).get(section)

    def get_form_overview(self, form_code: str) -> Optional[Dict]:
        """Get overview of entire form"""
        return self.form_schemas.get(form_code)

    def get_triggered_forms(self, form_code: str, field: str, value: str) -> List[str]:
        """Check if answering a field triggers additional required forms"""
        if form_code not in self.form_triggers:
            return []

        form_triggers = self.form_triggers[form_code]
        field_key = f"field_{field}"

        if field_key not in form_triggers:
            return []

        trigger_info = form_triggers[field_key]
        triggered_forms = []

        if 'values' in trigger_info and value in trigger_info['values']:
            triggered_forms.extend(trigger_info.get('triggers', []))

        return triggered_forms

    def search_form_knowledge_in_rag(self, form_code: str, query: str) -> str:
        """Search official documents for form-specific information"""
        try:
            # Enhanced query with form context
            enhanced_query = f"{form_code} form: {query}"

            results = vector_store.search(enhanced_query, k=2)

            if results:
                context = '\n\n'.join([doc.page_content[:500] for doc in results])
                return context

            return ""
        except Exception as e:
            print(f"RAG search error: {e}")
            return ""

    def generate_field_response(self, form_code: str, field: str,
                                user_question: str, conversation_history: List = None) -> Dict:
        """Generate response for field-specific question"""

        field_data = self.get_field_guidance(form_code, field)

        if not field_data:
            return {
                'success': False,
                'error': f'Field {field} not found in {form_code} form'
            }

        # Build context from structured knowledge
        context_parts = []

        # Form and field basics
        form_name = self.form_schemas[form_code]['name']
        context_parts.append(f"Form: {form_name} ({form_code})")
        context_parts.append(f"Field {field}: {field_data.get('label', 'Unknown field')}")

        if 'description' in field_data:
            context_parts.append(f"Purpose: {field_data['description']}")

        # Tips and guidance
        if 'tips' in field_data:
            context_parts.append("\nGuidance:")
            for tip in field_data['tips']:
                context_parts.append(f"• {tip}")

        # Common mistakes
        if 'mistakes' in field_data:
            context_parts.append("\nCommon mistakes to avoid:")
            for mistake in field_data['mistakes']:
                context_parts.append(f"• {mistake}")

        # Examples
        if 'example' in field_data:
            context_parts.append(f"\nExample: {field_data['example']}")

        if 'options' in field_data:
            context_parts.append("\nOptions:")
            for option in field_data['options']:
                context_parts.append(f"• {option}")

        # Triggers
        if 'triggers' in field_data:
            context_parts.append("\nImportant:")
            for trigger_key, trigger_actions in field_data['triggers'].items():
                for action in trigger_actions:
                    context_parts.append(f"• If you select '{trigger_key}': {action}")

        # RAG search for official documentation
        rag_context = self.search_form_knowledge_in_rag(form_code, user_question)
        if rag_context:
            context_parts.append("\nOfficial documentation reference:")
            context_parts.append(rag_context)

        structured_context = '\n'.join(context_parts)

        # Build conversation context
        conv_context = ""
        if conversation_history and len(conversation_history) > 1:
            recent = conversation_history[-4:]
            conv_lines = []
            for msg in recent:
                role = "User" if msg['role'] == 'user' else "Assistant"
                content = msg['content'][:120]
                conv_lines.append(f"{role}: {content}")
            conv_context = f"\n\nRecent conversation:\n{chr(10).join(conv_lines)}"

        # Detect user language
        user_language = self._detect_language(user_question)

        # Create system prompt
        if user_language == 'de':
            system_prompt = f"""Du bist Amtly, ein KI-Assistent für deutsche Formulare.{conv_context}

FORMULAR-KONTEXT:
{structured_context}

AUFGABE:
Beantworte die Frage des Benutzers zu diesem Formularfeld.
- Sei spezifisch und praktisch
- Erkläre klar, was einzutragen ist
- Warne vor häufigen Fehlern
- Gib Beispiele wenn hilfreich
- Erwähne zusätzliche erforderliche Formulare
"""
        else:
            system_prompt = f"""You are Amtly, an AI assistant for German bureaucracy forms.{conv_context}

FORM CONTEXT:
{structured_context}

TASK:
Answer the user's question about this form field.
- Be specific and practical
- Explain clearly what to enter
- Warn about common mistakes
- Give examples when helpful
- Mention additional required forms
"""

        try:
            result = openai_service.get_response(user_question, system_prompt)

            if result['success']:
                return {
                    'success': True,
                    'response': result['response'],
                    'form': form_code,
                    'field': field,
                    'metadata': {
                        'field_label': field_data.get('label'),
                        'required': field_data.get('required', False),
                        'critical': field_data.get('critical', False)
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def generate_section_response(self, form_code: str, section: str,
                                  user_question: str, conversation_history: List = None) -> Dict:
        """Generate response for section-level question"""

        section_data = self.get_section_guidance(form_code, section)

        if not section_data:
            return {
                'success': False,
                'error': f'Section {section} not found in {form_code} form'
            }

        # Build context
        form_name = self.form_schemas[form_code]['name']
        section_name = section_data.get('name', f'Section {section}')

        context_parts = [
            f"Form: {form_name} ({form_code})",
            f"Section {section}: {section_name}",
            ""
        ]

        # List fields in section
        fields = section_data.get('fields', {})
        if fields:
            context_parts.append("Fields in this section:")
            for field_key, field_data in fields.items():
                label = field_data.get('label', 'Unknown')
                context_parts.append(f"• Field {field_key}: {label}")

        structured_context = '\n'.join(context_parts)

        # Detect language
        user_language = self._detect_language(user_question)

        # Create system prompt
        if user_language == 'de':
            system_prompt = f"""Du bist Amtly, ein KI-Assistent für deutsche Formulare.

FORMULAR-KONTEXT:
{structured_context}

AUFGABE:
Erkläre diesen Abschnitt des Formulars und hilf dem Benutzer beim Ausfüllen.
- Gib einen Überblick über den Abschnitt
- Erkläre, welche Informationen benötigt werden
- Gib praktische Tipps
"""
        else:
            system_prompt = f"""You are Amtly, an AI assistant for German bureaucracy forms.

FORM CONTEXT:
{structured_context}

TASK:
Explain this section of the form and help the user fill it out.
- Give an overview of the section
- Explain what information is needed
- Provide practical tips
"""

        try:
            result = openai_service.get_response(user_question, system_prompt)

            if result['success']:
                return {
                    'success': True,
                    'response': result['response'],
                    'form': form_code,
                    'section': section
                }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def generate_form_overview_response(self, form_code: str,
                                        user_question: str, conversation_history: List = None) -> Dict:
        """Generate response for form-level question"""

        form_data = self.get_form_overview(form_code)

        if not form_data:
            return {
                'success': False,
                'error': f'Form {form_code} not found'
            }

        # Build context
        context_parts = [
            f"Form: {form_data['name']} ({form_code})",
            f"Purpose: {form_data['purpose']}",
            f"Total pages: {form_data.get('total_pages', 'Unknown')}",
            ""
        ]

        # List sections
        if 'sections' in form_data:
            context_parts.append("Sections:")
            for section_code, section_data in form_data['sections'].items():
                section_name = section_data.get('name', f'Section {section_code}')
                context_parts.append(f"• Section {section_code}: {section_name}")

        # Required documents
        if 'required_documents' in form_data:
            context_parts.append("\nRequired documents:")
            for doc in form_data['required_documents']:
                context_parts.append(f"• {doc}")

        # Critical notes
        if 'critical_notes' in form_data:
            context_parts.append("\nImportant notes:")
            for note in form_data['critical_notes']:
                context_parts.append(f"• {note}")

        structured_context = '\n'.join(context_parts)

        # Detect language
        user_language = self._detect_language(user_question)

        # Create system prompt
        if user_language == 'de':
            system_prompt = f"""Du bist Amtly, ein KI-Assistent für deutsche Formulare.

FORMULAR-KONTEXT:
{structured_context}

AUFGABE:
Erkläre dieses Formular und hilf dem Benutzer, es zu verstehen.
- Gib einen Überblick über das Formular
- Erkläre den Zweck
- Liste wichtige Abschnitte auf
- Erwähne erforderliche Dokumente
- Gib praktische Tipps zum Ausfüllen
"""
        else:
            system_prompt = f"""You are Amtly, an AI assistant for German bureaucracy forms.

FORM CONTEXT:
{structured_context}

TASK:
Explain this form and help the user understand it.
- Give an overview of the form
- Explain its purpose
- List important sections
- Mention required documents
- Provide practical filling tips
"""

        try:
            result = openai_service.get_response(user_question, system_prompt)

            if result['success']:
                return {
                    'success': True,
                    'response': result['response'],
                    'form': form_code
                }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def help_with_form(self, user_message: str, conversation_history: List = None) -> Dict:
        """Main entry point for form help"""

        # Detect what user is asking about
        detection = self.detect_form_and_field(user_message)

        form_code = detection['form_code']
        field = detection['field']
        section = detection['section']

        # Route to appropriate handler
        if form_code and field:
            # Specific field question
            return self.generate_field_response(
                form_code, field, user_message, conversation_history
            )

        elif form_code and section:
            # Section-level question
            return self.generate_section_response(
                form_code, section, user_message, conversation_history
            )

        elif form_code:
            # Form-level question
            return self.generate_form_overview_response(
                form_code, user_message, conversation_history
            )

        else:
            # Generic form question - use general guidance
            return self._handle_generic_form_question(user_message, conversation_history)

    def _handle_generic_form_question(self, user_message: str,
                                      conversation_history: List = None) -> Dict:
        """Handle questions that don't specify a particular form"""

        user_language = self._detect_language(user_message)

        # Build context from conversation if available
        conv_context = ""
        if conversation_history and len(conversation_history) > 1:
            recent = conversation_history[-4:]
            conv_lines = []
            for msg in recent:
                role = "User" if msg['role'] == 'user' else "Assistant"
                content = msg['content'][:120]
                conv_lines.append(f"{role}: {content}")
            conv_context = f"\n\nRecent conversation:\n{chr(10).join(conv_lines)}"

        # General form knowledge
        forms_list = "\n".join([
            f"• {code}: {data['name']} - {data['purpose']}"
            for code, data in self.form_schemas.items()
        ])

        if user_language == 'de':
            system_prompt = f"""Du bist Amtly, ein KI-Assistent für deutsche Formulare.{conv_context}

Verfügbare Formulare:
{forms_list}

AUFGABE:
Beantworte die Frage des Benutzers zu deutschen Jobcenter-Formularen.
- Wenn unklar welches Formular gemeint ist, frage nach
- Gib spezifische, praktische Ratschläge
- Erkläre klar und verständlich
"""
        else:
            system_prompt = f"""You are Amtly, an AI assistant for German bureaucracy forms.{conv_context}

Available forms:
{forms_list}

TASK:
Answer the user's question about German Jobcenter forms.
- If unclear which form, ask for clarification
- Give specific, practical advice
- Explain clearly and understandably
"""

        try:
            result = openai_service.get_response(user_message, system_prompt)

            if result['success']:
                return {
                    'success': True,
                    'response': result['response'],
                    'type': 'general_form_help'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        german_words = ['wie', 'was', 'wo', 'wann', 'ich', 'mein', 'das', 'ist', 'formular', 'feld']
        english_words = ['how', 'what', 'where', 'when', 'my', 'the', 'is', 'form', 'field']

        text_lower = text.lower()

        german_count = sum(1 for word in german_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)

        return 'de' if german_count > english_count else 'en'


# Create global instance
enhanced_form_helper = EnhancedFormHelper()