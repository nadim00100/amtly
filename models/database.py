from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Chat(db.Model):
    """Chat session model"""
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default="New Chat")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Current form context for session memory
    current_form = db.Column(db.String(50), nullable=True)
    document_context = db.Column(db.Text, nullable=True)  # For uploaded documents

    # Relationship with messages
    messages = db.relationship('Message', backref='chat', lazy=True,
                               cascade='all, delete-orphan',
                               order_by='Message.timestamp')

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'current_form': self.current_form,
            'message_count': len(self.messages)
        }

    def get_preview_message(self):
        """Get the first user message as preview"""
        for message in self.messages:
            if message.role == 'user' and len(message.content) > 0:
                return message.content[:60] + "..." if len(message.content) > 60 else message.content
        return "New conversation"

    def update_title_from_first_message(self):
        """Smart auto-generate title from first user message (ChatGPT style)"""
        first_user_message = None
        for message in self.messages:
            if message.role == 'user':
                first_user_message = message.content
                break

        if first_user_message:
            self.title = self._generate_smart_title(first_user_message)
        else:
            time_str = datetime.now().strftime("%H:%M")
            self.title = f"Chat {time_str}"

    def _generate_smart_title(self, message):
        """Generate ChatGPT/Claude style names (clean, 2-3 words)"""
        msg = message.lower().strip()

        # Topic-based names (exactly like ChatGPT)
        topics = {
            # German bureaucracy
            'bürgergeld': 'Bürgergeld Help',
            'arbeitslosengeld': 'Unemployment Benefits',
            'jobcenter': 'Jobcenter Questions',
            'sozialamt': 'Social Services',
            'krankenkasse': 'Health Insurance',
            'miete': 'Housing Costs',
            'wohnung': 'Housing Help',

            # Forms & Applications
            'antrag': 'Application Help',
            'formular': 'Form Help',
            'hauptantrag': 'Main Application',
            'weiterbewilligung': 'Renewal Application',
            'wba': 'WBA Form',
            'vm': 'VM Form',
            'kdu': 'KDU Form',
            'ha': 'HA Form',
            'ek': 'EK Form',

            # Communication
            'email': 'Email Writing',
            'brief': 'Letter Writing',
            'schreiben': 'Writing Help',
            'übersetzen': 'Translation',
            'translate': 'Translation',
            'document': 'Document Help',
            'dokument': 'Document Help',

            # English terms
            'form': 'Form Help',
            'application': 'Application Help',
            'benefits': 'Benefits Info',
            'eligibility': 'Eligibility Check',
            'payment': 'Payment Info',
            'housing': 'Housing Help',
            'unemployment': 'Unemployment Help',
        }

        # Find topic match
        for keyword, title in topics.items():
            if keyword in msg:
                return title

        # Question pattern matching
        if any(phrase in msg for phrase in ['how much', 'wie viel', 'wieviel']):
            return 'Amount Questions'
        elif any(phrase in msg for phrase in ['what is', 'was ist']):
            return 'Info Request'
        elif any(phrase in msg for phrase in ['how to', 'wie kann ich', 'wie mache ich']):
            return 'How-to Guide'
        elif any(phrase in msg for phrase in ['when', 'wann']):
            return 'Timing Questions'
        elif any(phrase in msg for phrase in ['where', 'wo']):
            return 'Location Help'
        elif any(phrase in msg for phrase in ['eligible', 'berechtigt', 'anspruch']):
            return 'Eligibility Check'
        elif any(phrase in msg for phrase in ['help', 'hilfe']):
            return 'General Help'
        elif any(phrase in msg for phrase in ['explain', 'erklären', 'erkläre']):
            return 'Explanation Request'
        elif any(phrase in msg for phrase in ['difference', 'unterschied']):
            return 'Comparison Help'

        # Extract first meaningful word + "Help"
        import re
        # Remove common stop words
        clean_msg = re.sub(
            r'\b(ich|mir|mich|der|die|das|ein|eine|ist|sind|can|i|the|a|an|is|are|do|does|how|what|when|where|why|help|hilfe|please|bitte)\b',
            '', msg)
        words = [w for w in clean_msg.split() if len(w) > 3]

        if words:
            return f"{words[0].title()} Help"

        # Final fallback
        return "New Chat"


class Message(db.Model):
    """Individual message model"""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)

    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Metadata
    sources = db.Column(db.Text, nullable=True)  # JSON string of sources
    message_type = db.Column(db.String(20), default='chat')  # 'chat', 'document', 'form', etc.
    used_knowledge_base = db.Column(db.Boolean, default=False)
    file_info = db.Column(db.Text, nullable=True)  # JSON string for uploaded file info

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'sources': json.loads(self.sources) if self.sources else [],
            'type': self.message_type,
            'used_knowledge_base': self.used_knowledge_base,
            'file_info': json.loads(self.file_info) if self.file_info else None
        }

    def set_sources(self, sources_list):
        """Set sources as JSON string"""
        if sources_list:
            self.sources = json.dumps(sources_list)
        else:
            self.sources = None

    def set_file_info(self, file_info_dict):
        """Set file info as JSON string"""
        if file_info_dict:
            self.file_info = json.dumps(file_info_dict)
        else:
            self.file_info = None


def init_database(app):
    """Initialize database with app"""
    db.init_app(app)

    with app.app_context():
        # Create tables
        db.create_all()

        print("📊 Database initialized successfully!")

        # Check if we have any chats
        chat_count = Chat.query.count()
        message_count = Message.query.count()

        print(f"📈 Database stats: {chat_count} chats, {message_count} messages")

        return db


def get_or_create_default_chat():
    """Get the most recent chat or create a new one"""
    latest_chat = Chat.query.order_by(Chat.updated_at.desc()).first()

    if not latest_chat:
        # Create first chat
        latest_chat = Chat(title="New Chat")
        db.session.add(latest_chat)
        db.session.commit()
        print(f"📝 Created first chat: {latest_chat.id}")

    return latest_chat


def create_new_chat(title=None):
    """Create a new chat session with ChatGPT-style default title"""
    if not title:
        title = "New Chat"  # Simple like ChatGPT/Claude

    chat = Chat(title=title)
    db.session.add(chat)
    db.session.commit()
    print(f"📝 Created new chat: {chat.id} - {title}")
    return chat


def add_message_to_chat(chat_id, role, content, sources=None, message_type='chat',
                        used_knowledge_base=False, file_info=None):
    """Add a message to a chat with debug naming"""

    # Get chat and count existing user messages BEFORE adding new one
    chat = Chat.query.get(chat_id)
    if not chat:
        return None

    current_user_messages = Message.query.filter_by(chat_id=chat_id, role='user').count()
    print(f"🐛 DEBUG: Chat {chat_id} has {current_user_messages} user messages")

    # Create message
    message = Message(
        chat_id=chat_id,
        role=role,
        content=content,
        message_type=message_type,
        used_knowledge_base=used_knowledge_base
    )

    if sources:
        message.set_sources(sources)
    if file_info:
        message.set_file_info(file_info)

    db.session.add(message)
    chat.updated_at = datetime.utcnow()

    # NAMING: Only for first user message
    if role == 'user' and current_user_messages == 0:
        old_title = chat.title
        new_title = chat._generate_smart_title(content)
        chat.title = new_title
        print(f"📝 NAMING: '{old_title}' → '{new_title}'")

    db.session.commit()
    return message


def get_chat_messages(chat_id, limit=100):
    """Get messages for a specific chat"""
    messages = Message.query.filter_by(chat_id=chat_id) \
        .order_by(Message.timestamp.asc()) \
        .limit(limit).all()
    return [msg.to_dict() for msg in messages]


def get_all_chats(limit=50):
    """Get all chats ordered by last update"""
    chats = Chat.query.order_by(Chat.updated_at.desc()).limit(limit).all()
    return [chat.to_dict() for chat in chats]


def delete_chat(chat_id):
    """Delete a chat and all its messages"""
    chat = Chat.query.get(chat_id)
    if chat:
        db.session.delete(chat)
        db.session.commit()
        return True
    return False


def update_chat_context(chat_id, current_form=None, document_context=None):
    """Update chat context for session memory"""
    chat = Chat.query.get(chat_id)
    if chat:
        if current_form is not None:
            chat.current_form = current_form
        if document_context is not None:
            chat.document_context = document_context

        db.session.commit()
        return True
    return False