from services.openai_service import openai_service


class SimpleFormHelper:
    """Form helper with IMPROVED detection - FIXED VERSION"""

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
        """IMPROVED - Only detect ACTUAL form-filling questions, not general info"""
        if not user_message:
            return False

        message_lower = user_message.lower().strip()

        # STEP 1: Check for general information questions FIRST (highest priority)
        # These should NEVER go to form help
        general_patterns = [
            # Amount/eligibility questions
            ('how much', 'wie viel', 'wieviel', 'how many', 'wie viele'),
            ('what is the amount', 'was ist der betrag', 'what amount', 'welcher betrag'),

            # Definition/explanation questions
            ('what is', 'was ist', 'what are', 'was sind'),
            ('define', 'definiere', 'definition'),
            ('explain', 'erklär', 'erkläre', 'erklären'),
            ('tell me about', 'erzähle mir', 'information about', 'informationen über'),

            # Eligibility questions
            ('am i eligible', 'bin ich berechtigt', 'habe ich anspruch'),
            ('do i qualify', 'kann ich bekommen', 'bekomme ich'),
            ('entitled to', 'berechtigt zu'),

            # Timing questions
            ('when do i get', 'wann bekomme ich', 'wann erhalte ich'),
            ('when is', 'wann ist', 'how long', 'wie lange'),

            # Process questions
            ('what happens', 'was passiert', 'how does', 'wie funktioniert'),
        ]

        for patterns in general_patterns:
            if any(pattern in message_lower for pattern in patterns):
                return False  # Route to RAG, not form help

        # STEP 2: Check for specific form references
        specific_forms = ['wba', 'ha', 'vm', 'kdu', 'ek', 'hauptantrag', 'weiterbewilligung','wep']
        has_specific_form = any(form in message_lower for form in specific_forms)

        # STEP 3: Check for explicit form identifiers
        form_identifiers = [
            'form', 'formular', 'formulär', 'antrag',
            'field', 'feld', 'section', 'abschnitt',
            'zeile', 'box', 'teil', 'bereich'
        ]
        has_form_identifier = any(word in message_lower for word in form_identifiers)

        # STEP 4: Check for form-filling action words
        form_actions = [
            'fill out', 'ausfüllen', 'fill in', 'eintragen',
            'how to fill', 'wie ausfüllen', 'wie fülle ich',
            'complete the form', 'vervollständigen',
            'help with form', 'hilfe bei formular', 'hilfe beim formular',
            'what does this field', 'was bedeutet dieses feld',
            'where do i write', 'wo schreibe ich', 'wo trage ich ein',
            'what do i put', 'was trage ich ein', 'which box', 'welches feld'
        ]
        has_form_action = any(action in message_lower for action in form_actions)

        # DECISION LOGIC
        # Only route to form help if:
        # 1. Has specific form name AND (form identifier OR form action), OR
        # 2. Has form identifier AND form action (without specific form)

        if has_specific_form and (has_form_identifier or has_form_action):
            return True

        if has_form_identifier and has_form_action:
            return True

        # Default: route to RAG/general
        return False

    def help_with_form(self, user_message, conversation_history=None):
        """Handle form-related questions with conversation context"""

        # Build system prompt with conversation awareness
        system_prompt = self.system_prompt

        # Add conversation context for follow-ups
        if conversation_history and len(conversation_history) > 1:
            recent = conversation_history[-4:]  # Last 4 messages
            conv_context = []

            for msg in recent:
                role = "User" if msg['role'] == 'user' else "Assistant"
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
- Maintain continuity with the previous discussion"""

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


# Create global instance
simple_form_helper = SimpleFormHelper()