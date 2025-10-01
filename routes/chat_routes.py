"""
Chat Routes - Main chat functionality and message processing
"""

from flask import Blueprint, request, jsonify, session
from models.database import (
    db, Chat, get_or_create_default_chat, add_message_to_chat,
    get_chat_messages, update_chat_context
)
from services.openai_service import openai_service
from services.language_detection import language_service
from core.chat_handler import rag_chat_handler
from core.document_processor import document_processor
from core.simple_form_helper import simple_form_helper
from utils.validation import validation_utils
from utils.response_formatter import response_formatter

chat_bp = Blueprint('chat', __name__)


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
    """Smart routing for user messages"""
    # 1. Check for explicit form questions
    is_form_question = simple_form_helper.detect_form_question(user_message)
    if is_form_question:
        return 'form'

    # 2. Check for German institution email requests
    is_german_institution_email = language_service.is_german_institution_request(user_message)
    if is_german_institution_email:
        return 'rag_german_email'

    # 3. Everything else goes to general RAG
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


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint - handles text messages and file uploads"""
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
        files = request.files.getlist('files')

        # Get context
        document_context = chat_obj.document_context or ''
        conversation_history = get_chat_messages(chat_id, limit=8)

        # Validation
        if not user_message and not files:
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
            if files:
                total_size = sum(file.content_length or 0 for file in files)
                file_info = {
                    'count': len(files),
                    'filenames': [file.filename for file in files],
                    'total_size': total_size
                }

            add_message_to_chat(
                chat_id=chat_id,
                role='user',
                content=user_message,
                file_info=file_info
            )

        response_text = ""
        sources = []
        message_type = 'chat'

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
        # PROCESS MULTIPLE UPLOADED FILES
        # ====================================================================
        if files:
            response_text, sources = process_uploaded_files(
                files, user_language, user_intent, conversation_history
            )

            if response_text:
                document_context = response_text[:4000]
                update_chat_context(chat_id, document_context=document_context)
                message_type = 'document'

        # ====================================================================
        # PROCESS TEXT MESSAGE
        # ====================================================================
        if user_message:
            text_response, text_sources, msg_type = process_text_message(
                user_message, document_context, user_language,
                conversation_history, response_text
            )

            if text_response:
                response_text = f"{response_text}\n\n---\n\n{text_response}" if response_text else text_response
                sources.extend(text_sources)
                if not files:
                    message_type = msg_type

        # Add assistant response to database
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
        import traceback
        traceback.print_exc()
        error_response = response_formatter.format_error_response(
            "An unexpected error occurred.", 'server_error'
        )
        return jsonify(error_response), 500


def process_uploaded_files(files, user_language, user_intent, conversation_history):
    """Process multiple uploaded files and return combined analysis"""
    try:
        all_extracted_texts = []
        processed_files = []

        for idx, file in enumerate(files):
            print(f"Processing file {idx + 1}/{len(files)}: {file.filename}")

            # Validate file
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)

            file_info_dict = {
                'name': file.filename,
                'size': file_size
            }

            is_valid, error = validation_utils.validate_file_upload(file_info_dict)
            if not is_valid:
                print(f"File {file.filename} validation failed: {error}")
                continue

            # Process document
            try:
                file_path = document_processor.save_uploaded_file(file)
                extracted_text = document_processor.process_document(file_path)
                file_path.unlink()

                if extracted_text:
                    all_extracted_texts.append({
                        'filename': file.filename,
                        'text': extracted_text,
                        'page_number': idx + 1
                    })
                    processed_files.append(file.filename)
                    print(f"✅ Extracted {len(extracted_text)} chars from {file.filename}")
            except Exception as e:
                print(f"❌ Error processing {file.filename}: {e}")
                continue

        # Check if we got any text
        if all_extracted_texts:
            # Combine all texts with page markers
            combined_text = ""
            for item in all_extracted_texts:
                if len(files) > 1:
                    combined_text += f"\n\n--- PAGE {item['page_number']} ({item['filename']}) ---\n\n"
                combined_text += item['text']

            # Build conversation context
            conv_context = ""
            if conversation_history and len(conversation_history) > 1:
                recent = conversation_history[-4:]
                conv_lines = [f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content'][:120]}"
                              for m in recent]
                conv_context = f"\n\nCONVERSATION CONTEXT:\n{chr(10).join(conv_lines)}"

            # Create system prompt
            if len(files) > 1:
                file_context = f"This is a multi-page document ({len(files)} pages/files). "
            else:
                file_context = "This is a document. "

            if user_language == 'de':
                if user_intent['explain'] and user_intent['translate']:
                    system_prompt = f"Du bist Amtly.{conv_context}\n\n{file_context}Erkläre UND übersetze dieses Dokument."
                elif user_intent['translate']:
                    system_prompt = f"Du bist Amtly.{conv_context}\n\n{file_context}Übersetze NUR (keine Erklärung)."
                else:
                    system_prompt = f"Du bist Amtly.{conv_context}\n\n{file_context}Erkläre das Dokument (NICHT übersetzen)."
            else:
                if user_intent['explain'] and user_intent['translate']:
                    system_prompt = f"You are Amtly.{conv_context}\n\n{file_context}Explain AND translate this document."
                elif user_intent['translate']:
                    system_prompt = f"You are Amtly.{conv_context}\n\n{file_context}Translate ONLY (no explanation)."
                else:
                    system_prompt = f"You are Amtly.{conv_context}\n\n{file_context}Explain the document (do NOT translate)."

            result = openai_service.get_response(
                f"Analyze this document:\n\n{combined_text[:3000]}",
                system_prompt
            )

            if result['success']:
                if len(files) > 1:
                    prefix = f"📄 **Multi-Page Document Analysis ({len(files)} pages):**\n\n"
                else:
                    prefix = "📄 **Document Analysis:**\n\n"
                response_text = prefix + result['response']
            else:
                response_text = "📄 Documents processed but had trouble analyzing them."

            return response_text, processed_files
        else:
            return "❌ Couldn't extract text from any files. Ensure documents are clear.", []

    except Exception as e:
        print(f"File processing error: {e}")
        return f"❌ Error processing files: {str(e)}", []


def process_text_message(user_message, document_context, user_language, conversation_history, existing_response):
    """Process text message through routing and RAG"""
    route = route_user_message(user_message, conversation_history)
    sources = []
    message_type = 'chat'

    # Try form helper first
    if route == 'form':
        form_result = simple_form_helper.help_with_form(
            user_message, conversation_history=conversation_history
        )

        if form_result['success']:
            response = f"📝 **Form Help:**\n\n{form_result['response']}"
            return response, sources, 'form'
        else:
            route = 'rag_general'

    # Try RAG
    if route.startswith('rag'):
        effective_language = 'de' if route == 'rag_german_email' else user_language

        try:
            rag_result = rag_chat_handler.generate_rag_response(
                user_message, document_context, effective_language,
                conversation_history=conversation_history
            )

            if rag_result and rag_result.get('success'):
                response = rag_result['response']
                if rag_result.get('sources'):
                    sources = rag_result['sources']
                return response, sources, 'chat'
            else:
                # Fallback to direct OpenAI
                response = handle_direct_openai_fallback(
                    user_message, effective_language, conversation_history
                )
                return response, sources, 'chat'

        except Exception as e:
            print(f"RAG error: {e}")
            response = handle_direct_openai_fallback(
                user_message, effective_language, conversation_history
            )
            return response, sources, 'chat'

    return "", sources, 'chat'


@chat_bp.route('/clear_session', methods=['POST'])
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