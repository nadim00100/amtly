"""
Amtly - AI-Powered German Bureaucracy Assistant
Main Application Entry Point
"""

from flask import Flask, render_template
from config import Config
from models.database import init_database, Chat, Message
from services.vector_store import vector_store


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

    # Register blueprints
    from routes.chat_routes import chat_bp
    from routes.api_routes import api_bp
    from routes.health_routes import health_bp

    app.register_blueprint(chat_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(health_bp)

    # Main route
    @app.route('/')
    def index():
        """Main chat interface"""
        return render_template('index.html')

    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('index.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from utils.response_formatter import response_formatter
        error_response = response_formatter.format_error_response("Internal server error", 'server_error')
        from flask import jsonify
        return jsonify(error_response), 500

    @app.errorhandler(413)
    def file_too_large(error):
        from utils.response_formatter import response_formatter
        error_response = response_formatter.format_error_response(
            "File too large. Maximum size is 16MB.", 'file_too_large'
        )
        from flask import jsonify
        return jsonify(error_response), 413

    return app


def print_startup_info(app):
    """Print application startup information"""
    print("=" * 70)
    print("🚀 Starting Amtly - AI-Powered German Bureaucracy Assistant")
    print("=" * 70)
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

    print(f"🌐 Server starting on http://localhost:8000")
    print("=" * 70)


if __name__ == '__main__':
    app = create_app()
    print_startup_info(app)
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=8000, threaded=True)