from flask import Flask, render_template, request, jsonify, session
from config import Config
from datetime import datetime

# Database imports
from models.database import (
    db, init_database, Chat, Message,
    create_new_chat, add_message_to_chat, get_chat_messages,
    get_all_chats, delete_chat, update_chat_context, get_or_create_default_chat
)

# Core AI services
from services.openai_service import openai_service
from services.vector_store import vector_store
from services.language_detection import language_service

# Core AI functionality
from core.chat_handler import rag_chat_handler
from core.document_processor import document_processor
from core.simple_form_helper import simple_form_helper

# Utilities
from utils.validation import validation_utils
from utils.response_formatter import response_formatter


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


def detect_user_intent(message):
    """Detect what user wants to do with the document"""
    if not message:
        return {'explain': True, 'translate': False}

    message_lower = message.lower()

    wants_explanation = any(word in message_lower for word in [
        'explain', 'erkläre', 'erklären', 'analyse', 'analyze',
        'what is', 'was ist', 'tell me', 'sag mir', 'describe', 'beschreib'
    ])

    wants_translation = any(word in message_lower for word in [
        'translate', 'übersetze', 'übersetz', 'translation', 'übersetzung',
        'in english', 'auf englisch', 'in german', 'auf deutsch'
    ])

    if not wants_explanation and not wants_translation:
        wants_explanation = True

    return {
        'explain': wants_explanation,
        'translate': wants_translation
    }


def route_user_message(user_message, conversation_history=None):
    """Smart routing for user messages - SIMPLIFIED VERSION"""

    # 1. Check for explicit form questions (very restrictive)
    is_form_question = simple_form_helper.detect_form_question(user_message)
    if is_form_question:
        return 'form'

    # 2. Check for German institution email requests
    is_german_institution_email = language_service.is_german_institution_request(user_message)
    if is_german_institution_email:
        return 'rag_german_email'

    # 3. Everything else goes to general RAG
    # Note: Document analysis is handled by file upload, not message routing
    return 'rag_general'


def handle_direct_openai_fallback(user_message, language, conversation_history=None):
    """Fallback when both form helper and RAG fail"""

    conv_context = ""
    if conversation_history and len(conversation_history) > 1:
        recent = conversation_history[-4:]
        conv_lines = []
        for msg in recent:
            role = "User" if msg['role'] == 'user' else "Assistant"
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            conv_lines.append(f"{role}: {content}")

        if language == 'de':
            conv_context = f"\n\nGESPRÄCHSKONTEXT:\n{chr(10).join(conv_lines)}"
        else:
            conv_context = f"\n\nCONVERSATION CONTEXT:\n{chr(10).join(conv_lines)}"

    if language == 'de':
        system_prompt = f"""Du bist Amtly, ein KI-Assistent für deutsche Bürokratie.{conv_context}

Du hilfst bei:
- Allgemeine Jobcenter-Fragen und -Regeln
- E-Mail-Verfassung (formeller deutscher Stil)
- Dokumentenübersetzung und -erklärung
- Bürokratische Prozesse und Vorschriften

Sei hilfreich, klar und professionell."""
    else:
        system_prompt = f"""You are Amtly, an AI assistant for German bureaucracy.{conv_context}

You help with:
- General Jobcenter questions and rules
- Email writing (formal German style)
- Document translation and explanation
- Bureaucratic processes and regulations

Be helpful, clear, and professional."""

    try:
        result = openai_service.get_response(user_message, system_prompt)
        return result['response'] if result['success'] else "❌ I encountered an error. Please try again."
    except Exception as e:
        print(f"OpenAI fallback error: {e}")
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


# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint - FIXED VERSION"""
    try:
        # Get chat_id
        chat_id = request.form.get('chat_id')
        if not chat_id:
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

        # Get context
        document_context = chat_obj.document_context or ''
        conversation_history = get_chat_messages(chat_id, limit=8)

        # Validation
        if not user_message and not file:
            error_response = response_formatter.format_error_response(
                "Please provide a message or upload a file.", 'validation_error'
            )
            return jsonify(error_response), 400

        if user_message:
            is_valid, error = validation_utils.validate_chat_message(user_message)
            if not is_valid:
                error_response = response_formatter.format_error_response(error, 'validation_error')
                return jsonify(error_response), 400

        # Add user message to database
        file_info = None
        if user_message:
            if file:
                # FIXED: Get file size without reading entire content
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset

                file_info = {
                    'filename': file.filename,
                    'size': file_size
                }

            add_message_to_chat(
                chat_id=chat_id,
                role='user',
                content=user_message,
                file_info=file_info
            )

        response_text = ""
        sources = []

        # Detect language and intent
        try:
            user_language = language_service.get_response_language(user_message) if user_message else 'en'
            user_intent = detect_user_intent(user_message) if user_message else {'explain': True, 'translate': False}
            is_german_institution_email = language_service.is_german_institution_request(
                user_message) if user_message else False
        except Exception as e:
            print(f"Language detection error: {e}")
            user_language = 'en'
            user_intent = {'explain': True, 'translate': False}
            is_german_institution_email = False

        if is_german_institution_email:
            user_language = 'de'

        # ====================================================================
        # PROCESS UPLOADED FILE (OCR + Analysis)
        # ====================================================================
        if file:
            try:
                # Validate file
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)

                file_info = {
                    'name': file.filename,
                    'size': file_size
                }

                is_valid, error = validation_utils.validate_file_upload(file_info)
                if not is_valid:
                    error_response = response_formatter.format_error_response(error, 'file_validation')
                    return jsonify(error_response), 400

                # Process document
                file_path = document_processor.save_uploaded_file(file)
                extracted_text = document_processor.process_document(file_path)
                file_path.unlink()  # Clean up

                if extracted_text:
                    # Store context
                    document_context = extracted_text[:4000]
                    update_chat_context(chat_id, document_context=document_context)

                    # Build conversation context
                    conv_context = ""
                    if conversation_history and len(conversation_history) > 1:
                        recent = conversation_history[-4:]
                        conv_lines = [f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content'][:120]}"
                                      for m in recent]
                        conv_context = f"\n\nCONVERSATION CONTEXT:\n{chr(10).join(conv_lines)}"

                    # Create system prompt based on intent
                    if user_language == 'de':
                        if user_intent['explain'] and user_intent['translate']:
                            system_prompt = f"Du bist Amtly.{conv_context}\n\nErkläre UND übersetze dieses Dokument."
                        elif user_intent['translate']:
                            system_prompt = f"Du bist Amtly.{conv_context}\n\nÜbersetze NUR (keine Erklärung)."
                        else:
                            system_prompt = f"Du bist Amtly.{conv_context}\n\nErkläre das Dokument (NICHT übersetzen)."
                    else:
                        if user_intent['explain'] and user_intent['translate']:
                            system_prompt = f"You are Amtly.{conv_context}\n\nExplain AND translate this document."
                        elif user_intent['translate']:
                            system_prompt = f"You are Amtly.{conv_context}\n\nTranslate ONLY (no explanation)."
                        else:
                            system_prompt = f"You are Amtly.{conv_context}\n\nExplain the document (do NOT translate)."

                    result = openai_service.get_response(
                        f"Analyze this document:\n\n{extracted_text[:2000]}",
                        system_prompt
                    )

                    if result['success']:
                        prefix = "📄 **Document Analysis:**\n\n"
                        response_text = prefix + result['response']
                    else:
                        response_text = "📄 Document processed but had trouble analyzing it."

                    sources.append(file.filename)
                else:
                    response_text = "❌ Couldn't extract text. Ensure document is clear."

            except Exception as e:
                print(f"File processing error: {e}")
                error_response = response_formatter.format_error_response(
                    f"Error processing file: {str(e)}", 'file_processing'
                )
                return jsonify(error_response), 400

        # ====================================================================
        # PROCESS TEXT MESSAGE (ROUTING + RAG + AI)
        # ====================================================================
        if user_message:
            route = route_user_message(user_message, conversation_history)

            if route == 'form':
                form_result = simple_form_helper.help_with_form(
                    user_message, conversation_history=conversation_history
                )

                if form_result['success']:
                    form_response = f"📝 **Form Help:**\n\n{form_result['response']}"
                    response_text = f"{response_text}\n\n---\n\n{form_response}" if response_text else form_response
                    message_type = 'form'
                else:
                    route = 'rag_general'

            if route.startswith('rag'):
                effective_language = 'de' if route == 'rag_german_email' else user_language

                try:
                    rag_result = rag_chat_handler.generate_rag_response(
                        user_message, document_context, effective_language,
                        conversation_history=conversation_history
                    )

                    if rag_result and rag_result.get('success'):
                        rag_response = rag_result['response']
                        response_text = f"{response_text}\n\n---\n\n{rag_response}" if response_text else rag_response

                        if rag_result.get('sources') and not sources:
                            sources.extend(rag_result['sources'])
                        elif rag_result.get('sources'):
                            rag_sources = rag_result.get('sources', [])
                            if rag_sources:
                                response_text += f"\n\n📚 *Additional references: {', '.join(rag_sources)}*"
                    else:
                        fallback = handle_direct_openai_fallback(
                            user_message, effective_language, conversation_history
                        )
                        response_text = f"{response_text}\n\n---\n\n{fallback}" if response_text else fallback

                except Exception as e:
                    print(f"RAG error: {e}")
                    fallback = handle_direct_openai_fallback(
                        user_message, effective_language, conversation_history
                    )
                    response_text = f"{response_text}\n\n---\n\n{fallback}" if response_text else fallback

        # Add assistant response to database
        message_type = 'document' if file else 'chat'
        if user_message and route == 'form':
            message_type = 'form'

        add_message_to_chat(
            chat_id=chat_id,
            role='assistant',
            content=response_text,
            sources=sources,
            message_type=message_type,
            used_knowledge_base=bool(sources)
        )

        # Format response
        formatted_response = response_formatter.format_chat_response(
            response_text,
            sources=sources if sources else [],
            response_type=message_type
        )

        formatted_response["chat_id"] = chat_id
        if document_context:
            formatted_response["document_text"] = document_context

        return jsonify(formatted_response)

    except Exception as e:
        print(f"Chat error: {e}")
        error_response = response_formatter.format_error_response(
            "An unexpected error occurred.", 'server_error'
        )
        return jsonify(error_response), 500


@app.route('/clear_session', methods=['POST'])
def clear_session():
    """Clear user session"""
    try:
        session.clear()
        return jsonify({"message": "Session cleared successfully", "status": "success"})
    except Exception as e:
        error_response = response_formatter.format_error_response(
            "Failed to clear session", 'session_error'
        )
        return jsonify(error_response), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health')
def health_check():
    """Application health check"""
    try:
        openai_configured = bool(Config.OPENAI_API_KEY)
        vector_info = vector_store.get_collection_info()

        with app.app_context():
            chat_count = Chat.query.count()
            message_count = Message.query.count()

        return jsonify({
            "status": "healthy",
            "openai_configured": openai_configured,
            "vector_store_documents": vector_info['count'],
            "database_chats": chat_count,
            "database_messages": message_count,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    error_response = response_formatter.format_error_response("Internal server error", 'server_error')
    return jsonify(error_response), 500


@app.errorhandler(413)
def file_too_large(error):
    error_response = response_formatter.format_error_response(
        "File too large. Maximum size is 16MB.", 'file_too_large'
    )
    return jsonify(error_response), 413


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    print("🚀 Starting Amtly - AI-Powered German Bureaucracy Assistant")
    print(f"📁 Data directory: {Config.DATA_DIR}")
    print(f"🤖 OpenAI configured: {bool(Config.OPENAI_API_KEY)}")

    try:
        info = vector_store.get_collection_info()
        print(f"📚 Knowledge base: {info['count']} documents loaded")
    except:
        print("📚 Knowledge base: Not initialized")

    with app.app_context():
        chat_count = Chat.query.count()
        message_count = Message.query.count()
        print(f"💬 Database: {chat_count} chats, {message_count} messages")

    print(f"🌐 Starting server on http://localhost:8000")
    print("=" * 50)

    app.run(debug=Config.DEBUG, host='0.0.0.0', port=8000, threaded=True)