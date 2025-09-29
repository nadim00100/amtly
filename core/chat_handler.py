from services.openai_service import openai_service
from services.vector_store import vector_store
from services.language_detection import language_service


class RAGChatHandler:
    """RAG Chat Handler - CLEANED VERSION"""

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
                    # FIXED: Better source validation
                    if source_name and isinstance(source_name, str):
                        clean_source = source_name.replace('.pdf', '').replace('.txt', '').strip()
                        # Only add valid sources
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
        """Generate response using RAG with conversation history"""

        # Detect language
        if requested_language:
            response_language = requested_language
            confidence = 'high'
        else:
            response_language = self.language_service.get_response_language(user_message)
            _, confidence, _ = self.language_service.detect_language(user_message)

        # Check for German institution email
        is_german_institution_email = self.language_service.is_german_institution_request(user_message)
        if is_german_institution_email:
            response_language = 'de'
            confidence = 'high'

        # Search knowledge base
        knowledge_result = self.search_knowledge_base(user_message)

        # Build context
        context_parts = []
        sources = []

        # Add recent conversation for follow-ups
        if conversation_history and len(conversation_history) > 1:
            context_parts.append("=== RECENT CONVERSATION ===")
            recent = conversation_history[-4:]
            conv_text = []
            for msg in recent:
                role = "User" if msg['role'] == 'user' else "Assistant"
                content = msg['content'][:150] + "..." if len(msg['content']) > 150 else msg['content']
                conv_text.append(f"{role}: {content}")
            context_parts.append('\n'.join(conv_text))

        # Add knowledge base context
        if knowledge_result:
            context_parts.append("=== OFFICIAL DOCUMENTS ===")
            context_parts.append(knowledge_result['context'])
            sources.extend(knowledge_result.get('sources', []))

        # Add document context
        if document_context:
            context_parts.append("=== UPLOADED DOCUMENT ===")
            context_parts.append(document_context)

        # Create system prompt
        system_prompt = self._create_system_prompt(
            response_language,
            is_german_institution_email,
            context_parts,
            confidence,
            has_conversation_history=bool(conversation_history and len(conversation_history) > 1)
        )

        # Get response
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
        """Create system prompt based on language and context"""

        full_context = '\n\n'.join(context_parts) if context_parts else ""
        lang_instruction = self.language_service.get_system_prompt_instruction(language, confidence)

        # Conversation awareness
        conversation_instruction = ""
        if has_conversation_history:
            if language == 'de':
                conversation_instruction = """
WICHTIG für Folgefragen:
- Du siehst die bisherige Unterhaltung im Kontext
- Bei Fragen wie "Wie viel?" beziehe dich auf das zuvor diskutierte Thema
- Bei E-Mail-Nachfragen wie "Mach es formeller" beziehe dich auf die vorherige E-Mail
- Halte den Gesprächsfluss aufrecht"""
            else:
                conversation_instruction = """
IMPORTANT for follow-ups:
- You can see the conversation history in context
- For questions like "How much?" refer to previously discussed topic
- For email follow-ups like "Make it formal" refer to previous email
- Maintain conversation flow"""

        # Base prompt
        if language == 'de':
            if is_german_institution_email:
                base_prompt = """Du bist Amtly, ein KI-Assistent für deutsche Bürokratie.
Du hilfst beim Verfassen von E-Mails an deutsche Behörden.

WICHTIG für E-Mails:
- Schreibe IMMER auf Deutsch
- Verwende formellen deutschen Behördenstil
- Struktur: Betreff, Anrede, Sachverhalt, Schlussformel
- Verwende "Sie" und formelle Sprache"""
            else:
                base_prompt = """Du bist Amtly, ein KI-Assistent für deutsche Bürokratie.
Du hilfst bei Jobcenter-Prozessen, Sozialleistungen und Formularen.
Antworte auf Deutsch und sei hilfreich, klar und professionell."""
        else:
            base_prompt = """You are Amtly, an AI assistant for German bureaucracy.
You help with Jobcenter processes, social services, and official forms.
Respond in English and be helpful, clear, and professional."""

        # Add context
        if full_context:
            if language == 'de':
                context_instruction = f"""
Nutze diese Informationen:
{full_context}

WICHTIG: 
- Basiere deine Antwort auf den Informationen
- Wenn Informationen fehlen, sage das klar
- Sei spezifisch und zitiere relevante Details"""
            else:
                context_instruction = f"""
Use this information:
{full_context}

IMPORTANT: 
- Base your answer on provided information
- If information is missing, say so clearly
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


# Create global instance
rag_chat_handler = RAGChatHandler()