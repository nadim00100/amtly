from flask import Flask, render_template, request, jsonify, session
from config import Config
from datetime import datetime
import re

# Database imports
from models.database import (
    db, init_database, Chat, Message,
    create_new_chat, add_message_to_chat, get_chat_messages,
    get_all_chats, delete_chat, update_chat_context, get_or_create_default_chat
)

# Core AI services
from services.openai_service import openai_service
from services.vector_store import vector_store

# Core AI functionality
from core.chat_handler import rag_chat_handler
from core.document_processor import document_processor
from core.simple_form_helper import simple_form_helper  # Simplified form system

# Keep utilities (as requested)
from utils.validation import validation_utils
from utils.response_formatter import response_formatter
from utils.file_utils import file_utils


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.FLASK_SECRET_KEY

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{Config.DATA_DIR}/amtly.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Create necessary directories
    Config.create_directories()

    # Initialize database
    init_database(app)

    return app


app = create_app()


def detect_german_institution_request(message):
    """Detect if user is asking for communication with German institutions"""
    if not message:
        return False

    message_lower = message.lower()

    # German institutions and bureaucratic entities
    german_institutions = [
        'jobcenter', 'arbeitsagentur', 'agentur für arbeit', 'bundesagentur',
        'sozialamt', 'bürgeramt', 'amt', 'behörde', 'krankenkasse', 'finanzamt',
        'ausländerbehörde', 'einwohnermeldeamt', 'jugendamt', 'familienkasse',
        'rentenversicherung', 'berufsgenossenschaft', 'arbeitsamt'
    ]

    # Email/letter indicators
    communication_words = [
        'email', 'e-mail', 'brief', 'letter', 'anschreiben', 'schreiben',
        'nachricht', 'message', 'write', 'schreib'
    ]

    has_institution = any(inst in message_lower for inst in german_institutions)
    has_communication = any(comm in message_lower for comm in communication_words)

    return has_institution and has_communication


def detect_user_language(message):
    """Detect if user is writing in German or English"""
    if not message:
        return 'en'

    message_lower = message.lower()

    # Common German words/phrases
    german_indicators = [
        'das', 'die', 'der', 'ist', 'und', 'mit', 'von', 'zu', 'auf', 'für',
        'was', 'wie', 'wo', 'wann', 'warum', 'welche', 'können', 'möchte',
        'bitte', 'danke', 'hallo', 'hilfe', 'formular', 'antrag', 'dokument',
        'übersetzen', 'erklären', 'jobcenter', 'bürgergeld', 'bescheid'
    ]

    # Count German indicators
    german_count = sum(1 for word in german_indicators if word in message_lower)
    total_words = len(message_lower.split())

    # If more than 20% German words or specific German phrases, assume German
    if german_count / max(total_words, 1) > 0.2 or german_count >= 2:
        return 'de'

    return 'en'


def detect_user_intent(message):
    """Detect what user wants to do with the document"""
    if not message:
        return {'explain': True, 'translate': False}  # Default to explain only

    message_lower = message.lower()

    # Check for explicit commands
    wants_explanation = any(word in message_lower for word in [
        'explain', 'erkläre', 'erklären', 'analyse', 'analyze',
        'what is', 'was ist', 'tell me', 'sag mir', 'describe', 'beschreib'
    ])

    wants_translation = any(word in message_lower for word in [
        'translate', 'übersetze', 'übersetz', 'translation', 'übersetzung',
        'in english', 'auf englisch', 'in german', 'auf deutsch', 'to english', 'to german'
    ])

    # If neither is explicitly mentioned, default based on context
    if not wants_explanation and not wants_translation:
        # If just uploading without specific request, explain only
        wants_explanation = True
        wants_translation = False

    return {
        'explain': wants_explanation,
        'translate': wants_translation
    }


def route_user_message(user_message, conversation_history=None):
    """Smart routing for user messages with debug logging"""

    print(f"🔍 ROUTING DEBUG: Message = '{user_message[:50]}...'")

    # 1. Check for explicit form questions (very restrictive)
    is_form_question = simple_form_helper.detect_form_question(user_message)
    print(f"📝 Form detection: {is_form_question}")

    if is_form_question:
        print("  → Routing to FORM HELPER")
        return 'form'

    # 2. Check for German institution email requests
    is_german_institution_email = detect_german_institution_request(user_message)
    print(f"✉️ German email detection: {is_german_institution_email}")

    if is_german_institution_email:
        print("  → Routing to RAG (German email mode)")
        return 'rag_german_email'

    # 3. Check for document analysis requests
    if any(word in user_message.lower() for word in
           ['translate', 'übersetzen', 'explain document', 'dokument erklären']):
        print("  → Routing to RAG (document analysis)")
        return 'rag_document'

    # 4. Default: General RAG for all other questions
    print("  → Routing to RAG (general)")
    return 'rag_general'


def handle_direct_openai_fallback(user_message, language, conversation_history=None):
    """Fallback when both form helper and RAG fail"""

    # Build conversation context
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

Nutze diesen Kontext für Folgefragen."""
        else:
            conv_context = f"""

CONVERSATION CONTEXT:
{chr(10).join(conv_lines)}

Use this context for follow-up questions."""

    if language == 'de':
        system_prompt = f"""Du bist Amtly, ein KI-Assistent für deutsche Bürokratie.{conv_context}

Du hilfst bei:
- Allgemeine Jobcenter-Fragen und -Regeln
- E-Mail-Verfassung (formeller deutscher Stil)
- Dokumentenübersetzung und -erklärung
- Bürokratische Prozesse und Vorschriften

Für konkrete Formular-Ausfüllhilfe verweise auf spezielle Formular-Tools.
Sei hilfreich, klar und professionell. Antworte auf Deutsch."""
    else:
        system_prompt = f"""You are Amtly, an AI assistant for German bureaucracy.{conv_context}

You help with:
- General Jobcenter questions and rules
- Email writing (formal German style)
- Document translation and explanation
- Bureaucratic processes and regulations

For specific form-filling help, refer to specialized form tools.
Be helpful, clear, and professional."""

    result = openai_service.get_response(user_message, system_prompt)

    if result['success']:
        return result['response']
    else:
        return "❌ I encountered an error. Please try again."


# ============================================================================
# CHAT MANAGEMENT API ROUTES
# ============================================================================

@app.route('/api/chats', methods=['GET'])
def get_chats():
    """Get all chat sessions"""
    try:
        chats = get_all_chats()
        return jsonify({
            'success': True,
            'chats': chats
        })
    except Exception as e:
        print(f"Error getting chats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chats', methods=['POST'])
def create_chat():
    """Create a new chat session"""
    try:
        data = request.get_json() or {}
        title = data.get('title', 'New Chat')

        chat = create_new_chat(title)

        return jsonify({
            'success': True,
            'chat': chat.to_dict()
        })
    except Exception as e:
        print(f"Error creating chat: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chats/<int:chat_id>', methods=['GET'])
def get_chat(chat_id):
    """Get a specific chat and its messages"""
    try:
        chat = db.session.get(Chat, chat_id)
        if not chat:
            return jsonify({'success': False, 'error': 'Chat not found'}), 404

        messages = get_chat_messages(chat_id)

        return jsonify({
            'success': True,
            'chat': chat.to_dict(),
            'messages': messages
        })
    except Exception as e:
        print(f"Error getting chat {chat_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chats/<int:chat_id>', methods=['DELETE'])
def delete_chat_endpoint(chat_id):
    """Delete a chat session"""
    try:
        success = delete_chat(chat_id)
        if success:
            return jsonify({'success': True, 'message': 'Chat deleted'})
        else:
            return jsonify({'success': False, 'error': 'Chat not found'}), 404
    except Exception as e:
        print(f"Error deleting chat {chat_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chats/<int:chat_id>/messages', methods=['GET'])
def get_chat_messages_endpoint(chat_id):
    """Get messages for a specific chat"""
    try:
        messages = get_chat_messages(chat_id)
        return jsonify({
            'success': True,
            'messages': messages
        })
    except Exception as e:
        print(f"Error getting messages for chat {chat_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint - RAG + Form Help + Document Processing with conversation history support"""
    try:
        # Get chat_id from form data or create new chat
        chat_id = request.form.get('chat_id')
        if not chat_id:
            # Create new chat or get default
            chat_obj = get_or_create_default_chat()
            chat_id = chat_obj.id
        else:
            chat_id = int(chat_id)
            chat_obj = db.session.get(Chat, chat_id)
            if not chat_obj:
                return jsonify({'error': 'Chat not found'}), 404

        # Get inputs
        user_message = request.form.get('message', '').strip() if request.form.get('message') else None
        file = request.files.get('file')

        # Get context from database
        document_context = chat_obj.document_context or ''

        # Get conversation history for follow-up questions (ALL pathways)
        conversation_history = get_chat_messages(chat_id, limit=8)  # Last 8 messages for context

        # Basic validation
        if not user_message and not file:
            error_response = response_formatter.format_error_response(
                "Please provide a message or upload a file.",
                'validation_error'
            )
            return jsonify(error_response), 400

        # Validate message if provided
        if user_message:
            is_valid, error = validation_utils.validate_chat_message(user_message)
            if not is_valid:
                error_response = response_formatter.format_error_response(error, 'validation_error')
                return jsonify(error_response), 400

        # Add user message to database
        file_info = None
        if user_message:
            if file:
                file_info = {
                    'filename': file.filename,
                    'size': len(file.read())
                }
                file.seek(0)  # Reset file pointer

            add_message_to_chat(
                chat_id=chat_id,
                role='user',
                content=user_message,
                file_info=file_info
            )

        response_text = ""
        sources = []

        # Detect user language, intent, and German institution requests
        user_language = detect_user_language(user_message) if user_message else 'en'
        user_intent = detect_user_intent(user_message) if user_message else {'explain': True, 'translate': False}
        is_german_institution_email = detect_german_institution_request(user_message) if user_message else False

        # Override language to German for German institution emails
        if is_german_institution_email:
            user_language = 'de'

        # ====================================================================
        # PROCESS UPLOADED FILE (OCR + Analysis) with conversation history
        # ====================================================================
        if file:
            try:
                # Validate file
                file_info = {
                    'name': file.filename,
                    'size': len(file.read())
                }
                file.seek(0)  # Reset file pointer

                is_valid, error = validation_utils.validate_file_upload(file_info)
                if not is_valid:
                    error_response = response_formatter.format_error_response(error, 'file_validation')
                    return jsonify(error_response), 400

                # Process document
                file_path = document_processor.save_uploaded_file(file)
                extracted_text = document_processor.process_document(file_path)
                file_path.unlink()  # Clean up

                if extracted_text:
                    # Store context in database
                    document_context = extracted_text[:4000]
                    update_chat_context(chat_id, document_context=document_context)

                    # Create system prompt with conversation awareness for documents
                    conv_context = ""
                    if conversation_history and len(conversation_history) > 1:
                        recent = conversation_history[-4:]
                        conv_lines = []
                        for msg in recent:
                            role = "User" if msg['role'] == 'user' else "Assistant"
                            content = msg['content'][:120] + "..." if len(msg['content']) > 120 else msg['content']
                            conv_lines.append(f"{role}: {content}")

                        if user_language == 'de':
                            conv_context = f"""

GESPRÄCHSKONTEXT (für Folgefragen zum Dokument):
{chr(10).join(conv_lines)}

Nutze diesen Kontext um Folgefragen zum Dokument zu beantworten."""
                        else:
                            conv_context = f"""

CONVERSATION CONTEXT (for document follow-up questions):
{chr(10).join(conv_lines)}

Use this context to answer follow-up questions about the document."""

                    # Create smart system prompt based on user intent and language with conversation awareness
                    if user_language == 'de':
                        if user_intent['explain'] and user_intent['translate']:
                            system_prompt = f"""Du bist Amtly, ein deutscher Bürokratie-Assistent.{conv_context}
                            Ein Benutzer hat ein Dokument hochgeladen und möchte sowohl eine Erklärung als auch eine Übersetzung.

                            Mach folgendes:
                            1. Erkläre auf Deutsch, worum es in diesem Dokument geht
                            2. Übersetze den Inhalt ins Deutsche (falls das Dokument in einer anderen Sprache ist) oder ins Englische (falls es auf Deutsch ist)
                            3. Hebe wichtige Informationen hervor

                            Sei hilfreich und klar."""
                        elif user_intent['translate']:
                            system_prompt = f"""Du bist Amtly, ein Übersetzungsassistent.{conv_context}
                            Ein Benutzer hat ein Dokument hochgeladen und möchte nur eine Übersetzung.

                            Übersetze den Dokumentinhalt ins Deutsche (falls in einer anderen Sprache) oder ins Englische (falls auf Deutsch).
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
                        if user_intent['explain'] and user_intent['translate']:
                            system_prompt = f"""You are Amtly, a German bureaucracy assistant.{conv_context}
                            A user has uploaded a document and wants both explanation and translation.

                            Please:
                            1. Explain what this document is about
                            2. Provide English translation of the content
                            3. Highlight important information or next steps

                            Be helpful and clear."""
                        elif user_intent['translate']:
                            system_prompt = f"""You are Amtly, a translation assistant.{conv_context}
                            A user has uploaded a document and wants only translation.

                            Translate the document content to English (if in German) or German (if in English).
                            Provide ONLY the translation, no additional explanations."""
                        else:  # explain only
                            system_prompt = f"""You are Amtly, a German bureaucracy assistant.{conv_context}
                            A user has uploaded a document and wants explanation only.

                            Explain in English:
                            1. What this document is about
                            2. Important information or next steps
                            3. Practical guidance for dealing with German bureaucracy

                            Do NOT translate, only explain. Be helpful and clear."""

                    result = openai_service.get_response(
                        f"Please analyze this document:\n\n{extracted_text[:2000]}",
                        system_prompt
                    )

                    if result['success']:
                        # Format response based on what was requested
                        if user_intent['explain'] and user_intent['translate']:
                            response_text = f"📄 **Document Analysis & Translation:**\n\n{result['response']}"
                        elif user_intent['translate']:
                            response_text = f"🌐 **Document Translation:**\n\n{result['response']}"
                        else:  # explain only
                            response_text = f"📄 **Document Analysis:**\n\n{result['response']}"
                    else:
                        response_text = "📄 **Document processed** but I had trouble analyzing it. You can ask me questions about it!"

                    # Set the uploaded file as the source
                    sources.append(file.filename)
                else:
                    response_text = "❌ I couldn't extract readable text from this document. Please ensure it's clear and well-scanned."

            except Exception as e:
                error_response = response_formatter.format_error_response(
                    f"Error processing file: {str(e)}",
                    'file_processing'
                )
                return jsonify(error_response), 400

        # ====================================================================
        # PROCESS TEXT MESSAGE (IMPROVED ROUTING + RAG + Natural AI) with conversation history
        # ====================================================================
        if user_message:
            # IMPROVED ROUTING with debug
            route = route_user_message(user_message, conversation_history)

            if route == 'form':
                # Handle specific form questions only
                form_result = simple_form_helper.help_with_form(
                    user_message,
                    conversation_history=conversation_history
                )

                if form_result['success']:
                    if response_text:
                        response_text += f"\n\n---\n\n📝 **Form Help:**\n\n{form_result['response']}"
                    else:
                        response_text = f"📝 **Form Help:**\n\n{form_result['response']}"

                    message_type = 'form'
                else:
                    # If form help fails, fall back to RAG
                    print("⚠️ Form help failed, falling back to RAG")
                    route = 'rag_general'

            if route.startswith('rag'):
                # Handle all non-form questions with RAG system
                effective_language = 'de' if route == 'rag_german_email' else user_language

                try:
                    rag_result = rag_chat_handler.generate_rag_response(
                        user_message,
                        document_context,
                        effective_language,
                        conversation_history=conversation_history
                    )

                    if rag_result and rag_result.get('success'):
                        if response_text:
                            response_text += f"\n\n---\n\n{rag_result['response']}"
                        else:
                            response_text = rag_result['response']

                        # Only add RAG sources if we don't already have document sources
                        if rag_result.get('sources') and not sources:
                            sources.extend(rag_result['sources'])
                        elif rag_result.get('sources') and sources:
                            # If we have document sources, add RAG sources separately
                            rag_sources = rag_result.get('sources', [])
                            if rag_sources:
                                response_text += f"\n\n📚 *Additional references: {', '.join(rag_sources)}*"
                    else:
                        # RAG failed, use direct OpenAI fallback
                        print("⚠️ RAG failed, using direct OpenAI fallback")
                        fallback_response = handle_direct_openai_fallback(user_message, effective_language,
                                                                          conversation_history)

                        if response_text:
                            response_text += f"\n\n---\n\n{fallback_response}"
                        else:
                            response_text = fallback_response

                except Exception as e:
                    # Final fallback to simple OpenAI if RAG fails
                    print(f"RAG failed with exception, using fallback: {e}")
                    fallback_response = handle_direct_openai_fallback(user_message, effective_language,
                                                                      conversation_history)

                    if response_text:
                        response_text += f"\n\n---\n\n{fallback_response}"
                    else:
                        response_text = fallback_response

        # Add assistant response to database
        message_type = 'document' if file else 'chat'
        if user_message and route == 'form':
            message_type = 'form'

        assistant_message = add_message_to_chat(
            chat_id=chat_id,
            role='assistant',
            content=response_text,
            sources=sources,
            message_type=message_type,
            used_knowledge_base=bool(sources)
        )

        # Format final response
        formatted_response = response_formatter.format_chat_response(
            response_text,
            sources=sources if sources else [],
            response_type=message_type
        )

        # Add chat context
        formatted_response["chat_id"] = chat_id
        if document_context:
            formatted_response["document_text"] = document_context

        return jsonify(formatted_response)

    except Exception as e:
        print(f"Chat error: {e}")
        error_response = response_formatter.format_error_response(
            "An unexpected error occurred. Please try again.",
            'server_error'
        )
        return jsonify(error_response), 500


# ============================================================================
# SESSION MANAGEMENT (Updated for database)
# ============================================================================

@app.route('/clear_session', methods=['POST'])
def clear_session():
    """Clear user session and document context"""
    try:
        session.clear()
        return jsonify({"message": "Session cleared successfully", "status": "success"})
    except Exception as e:
        error_response = response_formatter.format_error_response(
            "Failed to clear session",
            'session_error'
        )
        return jsonify(error_response), 500


# ============================================================================
# DEBUG AND HEALTH ROUTES
# ============================================================================

@app.route('/health')
def health_check():
    """Application health check"""
    try:
        # Check OpenAI configuration
        openai_configured = bool(Config.OPENAI_API_KEY)

        # Check vector store
        vector_info = vector_store.get_collection_info()
        vector_ready = vector_info['count'] > 0

        # Check directories
        directories_ready = all([
            Config.KNOWLEDGE_BASE_DIR.exists(),
            Config.UPLOADS_DIR.exists()
        ])

        # Check database
        with app.app_context():
            chat_count = Chat.query.count()
            message_count = Message.query.count()

        return jsonify({
            "status": "healthy",
            "openai_configured": openai_configured,
            "vector_store_documents": vector_info['count'],
            "vector_store_ready": vector_ready,
            "directories_ready": directories_ready,
            "database_chats": chat_count,
            "database_messages": message_count,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@app.route('/debug/knowledge_base')
def debug_knowledge_base():
    """Debug endpoint to inspect knowledge base"""
    try:
        info = vector_store.get_collection_info()

        # Test search
        test_results = vector_store.search("Bürgergeld", k=3)

        return jsonify({
            "vector_store_count": info['count'],
            "test_search_results": len(test_results),
            "status": "ready" if info['count'] > 0 else "empty",
            "sample_search": [
                {
                    "content": result.page_content[:100] + "...",
                    "source": result.metadata.get('source', 'unknown')
                }
                for result in test_results[:2]
            ]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/debug/routing')
def debug_routing():
    """Debug endpoint to test routing logic"""
    test_cases = [
        "Do I always need to be reachable by Jobcenter, or can I travel without telling?",  # Should be RAG
        "Help me fill out WBA form section B",  # Should be FORM
        "How do I fill in field 4.2 of the HA form?",  # Should be FORM
        "What is Bürgergeld?",  # Should be RAG
        "Write an email to Jobcenter about my application",  # Should be RAG (German email)
        "Wie viel Bürgergeld bekomme ich?",  # Should be RAG
        "Explain this document",  # Should be RAG (document)
        "Wie fülle ich das Formular aus?",  # Should be FORM
        "Was bedeutet Abschnitt 4.2 im Antrag?",  # Should be FORM
        "Muss ich erreichbar sein für das Jobcenter?",  # Should be RAG
    ]

    results = []
    for question in test_cases:
        route = route_user_message(question)
        results.append({
            'question': question,
            'route': route,
            'is_form': simple_form_helper.detect_form_question(question),
            'is_german_email': detect_german_institution_request(question)
        })

    return jsonify({
        'routing_tests': results,
        'total_tests': len(test_cases)
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    error_response = response_formatter.format_error_response(
        "Internal server error",
        'server_error'
    )
    return jsonify(error_response), 500


@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large errors"""
    error_response = response_formatter.format_error_response(
        "File too large. Maximum size is 16MB.",
        'file_too_large'
    )
    return jsonify(error_response), 413


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    print("🚀 Starting Amtly - AI-Powered German Bureaucracy Assistant")
    print(f"📁 Data directory: {Config.DATA_DIR}")
    print(f"🤖 OpenAI configured: {bool(Config.OPENAI_API_KEY)}")

    # Check vector store status
    try:
        info = vector_store.get_collection_info()
        print(f"📚 Knowledge base: {info['count']} documents loaded")
    except:
        print("📚 Knowledge base: Not initialized")

    # Check database status
    with app.app_context():
        chat_count = Chat.query.count()
        message_count = Message.query.count()
        print(f"💬 Database: {chat_count} chats, {message_count} messages")

    print(f"🌐 Starting server on http://localhost:8000")
    print("=" * 50)

    app.run(
        debug=Config.DEBUG,
        host='0.0.0.0',
        port=8000,
        threaded=True
    )