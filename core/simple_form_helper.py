from services.openai_service import openai_service


class SimpleFormHelper:
    def __init__(self):
        self.system_prompt = """You are a precise assistant for German Jobcenter forms and bureaucracy. 
You help users understand and fill out German government forms, especially Jobcenter and social services forms.

When helping with forms:
- Explain what each field/question is asking for
- Provide practical examples where helpful
- Give guidance on how to fill it correctly
- Mention any common mistakes to avoid
- Respond in the same language the user is using
- Be specific and actionable

For document translation and explanation:
- Translate accurately between German and English
- Explain bureaucratic terms in simple language
- Highlight important deadlines or requirements"""

    def detect_form_question(self, user_message):
        """Improved detection - only trigger on ACTUAL form questions, not general info questions"""
        if not user_message:
            return False

        message_lower = user_message.lower().strip()

        # PRIORITY 1: GENERAL QUESTIONS (must be checked FIRST)
        # These should NEVER go to form help
        general_question_patterns = [
            # Amount questions
            'how much', 'wie viel', 'wieviel', 'how many', 'wie viele',
            'what is the amount', 'was ist der betrag',
            'what amount', 'welcher betrag',

            # Definition questions
            'what is', 'was ist', 'what are', 'was sind',
            'define', 'definiere', 'definition',

            # Information questions
            'explain', 'erklär', 'erkläre', 'erklären',
            'tell me about', 'erzähle mir über', 'erzähl mir',
            'information about', 'informationen über','What happen', 'was passiert',

            # Eligibility questions
            'am i eligible', 'bin ich berechtigt', 'habe ich anspruch',
            'do i qualify', 'qualifiziere ich mich',
            'can i get', 'kann ich bekommen', 'bekomme ich',
            'entitled to', 'berechtigt zu',

            # Timing questions
            'when do i get', 'wann bekomme ich', 'wann erhalte ich',
            'when is', 'wann ist', 'when does', 'wann macht',
            'how long', 'wie lange',

            # Process questions (general)
            'how does', 'wie funktioniert', 'wie läuft',
            'what happens', 'was passiert', 'was geschieht',
            'what is the process', 'wie ist der prozess',
        ]

        # Check for general questions FIRST (highest priority)
        for pattern in general_question_patterns:
            if pattern in message_lower:
                return False  # Always route to RAG/general

        # PRIORITY 2: SPECIFIC FORM REFERENCES
        specific_forms = ['wba', 'ha', 'vm', 'kdu', 'ek', 'hauptantrag', 'weiterbewilligung']
        if any(form in message_lower for form in specific_forms):
            return True

        # PRIORITY 3: EXPLICIT FORM ACTION PATTERNS
        form_action_patterns = [
            # Filling out forms
            'fill out', 'ausfüllen', 'fill in', 'eintragen',
            'how to fill', 'wie ausfüllen', 'wie fülle ich',
            'complete the form', 'formular vervollständigen', 'vervollständigen',
            'how to complete', 'wie vervollständigen',

            # Form help requests
            'help with form', 'hilfe bei formular', 'hilfe beim formular',
            'help me with', 'hilf mir bei', 'hilf mir mit',

            # Form field questions
            'what does this field', 'was bedeutet dieses feld',
            'field means', 'feld bedeutet',
            'where do i write', 'wo schreibe ich', 'wo trage ich ein',
            'what do i put in', 'was trage ich ein', 'was schreibe ich',
            'which box', 'welches feld', 'welche zeile',

            # Form sections
            'section', 'abschnitt', 'teil', 'bereich',
            'field', 'feld', 'zeile', 'box',
        ]

        # Check for form actions
        has_form_action = any(pattern in message_lower for pattern in form_action_patterns)

        # PRIORITY 4: EXPLICIT FORM WORDS (only if combined with actions)
        explicit_form_words = ['form', 'formular', 'formulär', 'antrag', 'application']
        has_explicit_form = any(word in message_lower for word in explicit_form_words)

        # DECISION LOGIC
        # Only route to form help if:
        # 1. Has form actions, OR
        # 2. Has explicit form words AND form actions
        if has_form_action:
            return True
        if has_explicit_form and has_form_action:
            return True

        # Default: route to RAG/general
        return False

    def help_with_form(self, user_message, conversation_history=None):
        """Handle form-related questions with conversation context for follow-up questions"""

        # Build system prompt with conversation awareness
        system_prompt = self.system_prompt

        # Add conversation context for follow-ups
        if conversation_history and len(conversation_history) > 1:
            recent = conversation_history[-4:]  # Last 4 messages for context
            conv_context = []

            for msg in recent:
                role = "User" if msg['role'] == 'user' else "Assistant"
                # Limit content length to avoid token overuse
                content = msg['content'][:150] + "..." if len(msg['content']) > 150 else msg['content']
                conv_context.append(f"{role}: {content}")

            context_text = '\n'.join(conv_context)

            system_prompt += f"""

CONVERSATION CONTEXT (for follow-up questions):
{context_text}

IMPORTANT: Use the conversation context above to answer follow-up questions intelligently.
- If the user asks about "field 3" or "that section", refer to the previously discussed form
- If they ask "what does it mean?" or "how do I fill it?", refer to what was previously mentioned
- If they mention "the form" without specifying, use the form discussed in the conversation
- For questions like "make it simpler" or "explain differently", refer to your previous explanation
- Maintain continuity with the previous discussion about forms and bureaucracy"""

        try:
            result = openai_service.get_response(
                user_message,
                system_prompt,
                clean_context=True
            )

            if result['success']:
                return {
                    'success': True,
                    'response': result['response'],
                    'type': 'form_help'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }

        except Exception as e:
            return {
                'success': False,
                'error': f"Error getting form help: {str(e)}"
            }

    def explain_specific_field(self, form_name, field_name, user_question="", conversation_history=None):
        """Handle specific form field questions with conversation context"""

        # Build conversation context
        conv_context = ""
        if conversation_history and len(conversation_history) > 1:
            recent = conversation_history[-4:]
            conv_lines = []
            for msg in recent:
                role = "User" if msg['role'] == 'user' else "Assistant"
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                conv_lines.append(f"{role}: {content}")

            conv_context = f"""
CONVERSATION CONTEXT:
{chr(10).join(conv_lines)}

Use this context to provide more relevant and specific guidance."""

        user_prompt = f"""Form: {form_name}
Field/Question: {field_name}
Additional context: {user_question}
{conv_context}

Please explain what this field is asking for and how to fill it correctly. Include examples if helpful.
Consider the conversation context when providing your explanation."""

        try:
            result = openai_service.get_response(
                user_prompt,
                self.system_prompt,
                clean_context=True
            )

            if result['success']:
                return {
                    'success': True,
                    'response': result['response'],
                    'type': 'field_explanation'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }

        except Exception as e:
            return {
                'success': False,
                'error': f"Error explaining field: {str(e)}"
            }


# Create global instance
simple_form_helper = SimpleFormHelper()