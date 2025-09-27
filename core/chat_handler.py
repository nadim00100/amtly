from services.openai_service import openai_service
from services.vector_store import vector_store
from services.language_detection import language_service


class RAGChatHandler:
    def __init__(self):
        self.vector_store = vector_store
        self.openai_service = openai_service
        self.language_service = language_service

    def search_knowledge_base(self, query, k=3):
        """Search knowledge base for relevant information"""
        try:
            results = self.vector_store.search_with_scores(query, k=k)

            if not results:
                return None

            context_parts = []
            sources = set()

            for doc, score in results:
                context_parts.append(doc.page_content)
                if 'source' in doc.metadata:
                    source_name = doc.metadata['source']
                    # Clean source name and validate it
                    if source_name and isinstance(source_name, str):
                        clean_source = source_name.replace('.pdf', '').replace('.txt', '').strip()
                        # Only add if it's a real source, not placeholder
                        if clean_source and clean_source not in ['*', 'unknown', ''] and len(clean_source) > 1:
                            sources.add(clean_source)

            return {
                'context': '\n\n'.join(context_parts),
                'sources': list(sources),
                'chunks_found': len(results)
            }
        except Exception as e:
            print(f"Knowledge base search error: {e}")
            return None

    def generate_rag_response(self, user_message, document_context=None, requested_language=None,
                              conversation_history=None):
        """Generate response using RAG with improved language handling and conversation history"""

        # Detect user's preferred language
        if requested_language:
            response_language = requested_language
            confidence = 'explicit'
        else:
            response_language = self.language_service.get_response_language(user_message)
            _, confidence, _ = self.language_service.detect_language(user_message)

        # Check if this is a German institution email request (always German)
        is_german_institution_email = self.language_service.is_german_institution_request(user_message)
        if is_german_institution_email:
            response_language = 'de'
            confidence = 'high'

        # Search knowledge base
        knowledge_result = self.search_knowledge_base(user_message)

        # Build context with conversation history for follow-ups
        context_parts = []
        sources = []

        # Add recent conversation for follow-up questions
        if conversation_history and len(conversation_history) > 1:
            context_parts.append("=== RECENT CONVERSATION ===")
            # Get last 4 messages (2 exchanges) for context
            recent = conversation_history[-4:]
            conv_text = []
            for msg in recent:
                role = "User" if msg['role'] == 'user' else "Assistant"
                # Limit length to avoid token overuse
                content = msg['content'][:150] + "..." if len(msg['content']) > 150 else msg['content']
                conv_text.append(f"{role}: {content}")
            context_parts.append('\n'.join(conv_text))

        # Add knowledge base context
        if knowledge_result:
            context_parts.append("=== OFFICIAL DOCUMENTS ===")
            context_parts.append(knowledge_result['context'])
            sources.extend(knowledge_result.get('sources', []))

        # Add document context if available
        if document_context:
            context_parts.append("=== UPLOADED DOCUMENT ===")
            context_parts.append(document_context)

        # Create system prompt based on response language and request type
        system_prompt = self._create_system_prompt(
            response_language,
            is_german_institution_email,
            context_parts,
            confidence,
            has_conversation_history=bool(conversation_history and len(conversation_history) > 1)
        )

        # Get response from OpenAI
        try:
            result = self.openai_service.get_response(
                user_message,
                system_prompt,
                clean_context=True
            )

            if result['success']:
                return {
                    'success': True,
                    'response': result['response'],
                    'sources': sources,
                    'used_knowledge_base': bool(knowledge_result),
                    'detected_language': response_language,
                    'is_german_institution_email': is_german_institution_email
                }
            else:
                return {
                    'success': False,
                    'error': result['error'],
                    'response': self._get_error_message(response_language)
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': self._get_error_message(response_language)
            }

    def _create_system_prompt(self, language, is_german_institution_email, context_parts, confidence,
                              has_conversation_history=False):
        """Create appropriate system prompt based on language and context with conversation awareness"""

        # Base context
        full_context = '\n\n'.join(context_parts) if context_parts else ""

        # Language instruction
        lang_instruction = self.language_service.get_system_prompt_instruction(language, confidence)

        # Conversation awareness instruction
        conversation_instruction = ""
        if has_conversation_history:
            if language == 'de':
                conversation_instruction = """
WICHTIG für Folgefragen und E-Mail-Bearbeitung:
- Du siehst die bisherige Unterhaltung im Kontext oben
- Bei Fragen wie "Wie viel bekomme ich?" oder "Wann erhalte ich das?" beziehe dich auf das zuvor diskutierte Thema
- Bei E-Mail-Nachfragen wie "Mach es formeller" oder "Ändere den Ton" beziehe dich auf die zuvor geschriebene E-Mail
- Für E-Mail-Überarbeitungen: Nimm die vorherige E-Mail als Basis und passe sie entsprechend an
- Halte den Gesprächsfluss aufrecht und antworte im Kontext der bisherigen Unterhaltung"""
            else:
                conversation_instruction = """
IMPORTANT for follow-up questions and email editing:
- You can see the conversation history in the context above
- For questions like "How much do I get?" or "When do I receive it?" refer to the previously discussed topic
- For email follow-ups like "Make it more formal" or "Change the tone" refer to the previously written email
- For email revisions: Use the previous email as basis and modify accordingly
- Maintain conversation flow and answer in the context of the previous discussion"""

        if language == 'de':
            if is_german_institution_email:
                base_prompt = """Du bist Amtly, ein KI-Assistent spezialisiert auf deutsche Bürokratie.
Du hilfst beim Verfassen von E-Mails und Briefen an deutsche Behörden.

WICHTIG für E-Mails an deutsche Behörden:
- Schreibe IMMER auf Deutsch
- Verwende formellen deutschen Behördenstil
- Struktur: Betreff, höfliche Anrede, klarer Sachverhalt, höfliche Schlussformel
- Verwende "Sie" und formelle Sprache
- Sei respektvoll aber direkt

Beispiel-Struktur:
Betreff: [Klarer Betreff]
Sehr geehrte Damen und Herren,
[Hauptinhalt]
Mit freundlichen Grüßen
[Ihr Name]"""
            else:
                base_prompt = """Du bist Amtly, ein KI-Assistent spezialisiert auf deutsche Bürokratie.
Du hilfst Menschen bei Jobcenter-Prozessen, Sozialleistungen und offiziellen Formularen.
Antworte auf Deutsch und sei hilfreich, klar und professionell.

Du kannst helfen bei:
- Fragen zur deutschen Bürokratie
- Formular-Erklärungen
- Dokument-Übersetzungen
- E-Mail-Verfassung
- Allgemeine Unterstützung"""
        else:  # English
            base_prompt = """You are Amtly, an AI assistant specialized in German bureaucracy.
You help people navigate Jobcenter processes, social services, and official forms.
Respond in English and be helpful, clear, and professional.

You can help with:
- German bureaucracy questions
- Form explanations
- Document translations
- Email writing (in formal German style for German offices)
- General assistance"""

        # Add context if available
        if full_context:
            if language == 'de':
                context_instruction = f"""
Nutze diese Informationen für deine Antwort:
{full_context}

WICHTIG: 
- Basiere deine Antwort auf den bereitgestellten Informationen
- Wenn Informationen nicht in den Dokumenten stehen, sage das klar
- Konzentriere dich auf deutsche Bürokratie-Themen
- Sei spezifisch und zitiere relevante Details"""
            else:
                context_instruction = f"""
Use this information to answer:
{full_context}

IMPORTANT: 
- Base your answer on the provided information
- If information isn't in documents, say so clearly
- Focus on German bureaucracy topics
- Be specific and cite relevant details"""

            return f"{lang_instruction}\n\n{base_prompt}\n{conversation_instruction}\n{context_instruction}"
        else:
            return f"{lang_instruction}\n\n{base_prompt}\n{conversation_instruction}"

    def _get_error_message(self, language):
        """Get error message in appropriate language"""
        if language == 'de':
            return "Es ist ein Fehler aufgetreten. Bitte versuche es erneut."
        else:
            return "An error occurred. Please try again."

    def process_document_analysis(self, extracted_text, user_intent, language, filename=None,
                                  conversation_history=None):
        """Process document analysis with user intent, language preference, and conversation history"""

        # Build conversation context for document follow-ups
        conv_context = ""
        if conversation_history and len(conversation_history) > 1:
            recent = conversation_history[-4:]
            conv_lines = []
            for msg in recent:
                role = "User" if msg['role'] == 'user' else "Assistant"
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                conv_lines.append(f"{role}: {content}")

            if language == 'de':
                conv_context = f"""
GESPRÄCHSKONTEXT:
{chr(10).join(conv_lines)}

Nutze diesen Kontext um Folgefragen zum Dokument zu beantworten."""
            else:
                conv_context = f"""
CONVERSATION CONTEXT:
{chr(10).join(conv_lines)}

Use this context to answer follow-up questions about the document."""

        # Create system prompt based on user intent
        if language == 'de':
            if user_intent.get('explain') and user_intent.get('translate'):
                system_prompt = f"""Du bist Amtly, ein deutscher Bürokratie-Assistent.{conv_context}
Ein Benutzer hat ein Dokument hochgeladen und möchte sowohl eine Erklärung als auch eine Übersetzung.

Mach folgendes:
1. Erkläre auf Deutsch, worum es in diesem Dokument geht
2. Übersetze den Inhalt (ins Deutsche falls fremdsprachig, ins Englische falls deutsch)
3. Hebe wichtige Informationen hervor
4. Gib praktische nächste Schritte

Sei hilfreich und klar."""
            elif user_intent.get('translate'):
                system_prompt = f"""Du bist Amtly, ein Übersetzungsassistent für deutsche Bürokratie.{conv_context}
Ein Benutzer hat ein Dokument hochgeladen und möchte nur eine Übersetzung.

Übersetze den Dokumentinhalt:
- Ins Deutsche (falls in einer anderen Sprache) 
- Ins Englische (falls auf Deutsch)

Gib NUR die Übersetzung aus, keine zusätzlichen Erklärungen."""
            else:  # explain only
                system_prompt = f"""Du bist Amtly, ein deutscher Bürokratie-Assistent.{conv_context}
Ein Benutzer hat ein Dokument hochgeladen und möchte eine Erklärung.

Erkläre auf Deutsch:
1. Worum es in diesem Dokument geht
2. Wichtige Informationen oder nächste Schritte
3. Praktische Tipps für den Umgang mit deutschen Behörden

Übersetze NICHT, sondern erkläre nur. Sei hilfreich und klar."""
        else:  # English
            if user_intent.get('explain') and user_intent.get('translate'):
                system_prompt = f"""You are Amtly, a German bureaucracy assistant.{conv_context}
A user has uploaded a document and wants both explanation and translation.

Please:
1. Explain what this document is about
2. Provide translation of the content to English (if German) or German (if English)
3. Highlight important information or next steps
4. Give practical guidance

Be helpful and clear."""
            elif user_intent.get('translate'):
                system_prompt = f"""You are Amtly, a translation assistant for German bureaucracy.{conv_context}
A user has uploaded a document and wants only translation.

Translate the document content:
- To English (if in German)
- To German (if in English)

Provide ONLY the translation, no additional explanations."""
            else:  # explain only
                system_prompt = f"""You are Amtly, a German bureaucracy assistant.{conv_context}
A user has uploaded a document and wants explanation only.

Explain in English:
1. What this document is about
2. Important information or next steps
3. Practical guidance for dealing with German bureaucracy

Do NOT translate, only explain. Be helpful and clear."""

        # Process with OpenAI
        query = f"Please analyze this document{' (' + filename + ')' if filename else ''}:\n\n{extracted_text[:2000]}"

        result = self.openai_service.get_response(query, system_prompt)

        if result['success']:
            return {
                'success': True,
                'response': result['response'],
                'sources': [filename] if filename else [],
                'analysis_type': 'document_analysis'
            }
        else:
            return {
                'success': False,
                'error': result['error'],
                'response': self._get_error_message(language)
            }


# Create global instance
rag_chat_handler = RAGChatHandler()