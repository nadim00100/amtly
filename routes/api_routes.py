"""
API Routes - Chat management endpoints
"""

from flask import Blueprint, jsonify, request
from models.database import (
    db, Chat, create_new_chat, get_chat_messages,
    get_all_chats, delete_chat
)

api_bp = Blueprint('api', __name__)


@api_bp.route('/chats', methods=['GET'])
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


@api_bp.route('/chats', methods=['POST'])
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


@api_bp.route('/chats/<int:chat_id>', methods=['GET'])
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


@api_bp.route('/chats/<int:chat_id>', methods=['DELETE'])
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


@api_bp.route('/chats/<int:chat_id>/context', methods=['PUT'])
def update_chat_context_endpoint(chat_id):
    """Update chat context (form, document)"""
    try:
        from models.database import update_chat_context

        data = request.get_json() or {}
        current_form = data.get('current_form')
        document_context = data.get('document_context')

        success = update_chat_context(chat_id, current_form, document_context)

        if success:
            return jsonify({'success': True, 'message': 'Context updated'})
        else:
            return jsonify({'success': False, 'error': 'Chat not found'}), 404
    except Exception as e:
        print(f"Error updating context for chat {chat_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500