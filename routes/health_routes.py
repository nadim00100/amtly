"""
Health Routes - System health checks and status
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
from config import Config
from services.vector_store import vector_store
from models.database import Chat, Message

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """Application health check"""
    try:
        openai_configured = bool(Config.OPENAI_API_KEY)
        vector_info = vector_store.get_collection_info()

        with current_app.app_context():
            chat_count = Chat.query.count()
            message_count = Message.query.count()

        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "openai": {
                    "configured": openai_configured,
                    "model": Config.OPENAI_MODEL
                },
                "vector_store": {
                    "status": vector_info['status'],
                    "documents": vector_info['count']
                },
                "database": {
                    "chats": chat_count,
                    "messages": message_count
                }
            }
        })

    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@health_bp.route('/status')
def status():
    """Detailed system status"""
    try:
        vector_info = vector_store.get_collection_info()

        with current_app.app_context():
            chat_count = Chat.query.count()
            message_count = Message.query.count()

            # Get recent activity
            recent_chats = Chat.query.order_by(Chat.updated_at.desc()).limit(5).all()
            recent_activity = [{
                'id': chat.id,
                'title': chat.title,
                'updated_at': chat.updated_at.isoformat()
            } for chat in recent_chats]

        return jsonify({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "total_chats": chat_count,
                "total_messages": message_count,
                "recent_activity": recent_activity
            },
            "vector_store": {
                "total_documents": vector_info['count'],
                "collection_name": vector_info['name'],
                "status": vector_info['status']
            },
            "configuration": {
                "openai_model": Config.OPENAI_MODEL,
                "max_tokens": Config.MAX_TOKENS,
                "temperature": Config.TEMPERATURE,
                "supported_languages": Config.SUPPORTED_LANGUAGES
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@health_bp.route('/ping')
def ping():
    """Simple ping endpoint"""
    return jsonify({
        "status": "ok",
        "message": "pong",
        "timestamp": datetime.now().isoformat()
    })