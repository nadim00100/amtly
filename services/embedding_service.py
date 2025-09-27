from langchain_huggingface import HuggingFaceEmbeddings
from config import Config

# Global variable to ensure single loading
_EMBEDDINGS_INSTANCE = None
_LOADING_IN_PROGRESS = False


class EmbeddingService:
    def __init__(self):
        self.model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    @property
    def embeddings(self):
        """Lazy load embeddings only ONCE globally"""
        global _EMBEDDINGS_INSTANCE, _LOADING_IN_PROGRESS

        # Return existing instance if already loaded
        if _EMBEDDINGS_INSTANCE is not None:
            return _EMBEDDINGS_INSTANCE

        # Prevent duplicate loading if already in progress
        if _LOADING_IN_PROGRESS:
            import time
            while _LOADING_IN_PROGRESS:
                time.sleep(0.1)
            return _EMBEDDINGS_INSTANCE

        # Load embeddings
        _LOADING_IN_PROGRESS = True
        try:
            print("🔄 Loading embedding model... (this may take a moment)")
            _EMBEDDINGS_INSTANCE = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("✅ Embedding model loaded!")
        finally:
            _LOADING_IN_PROGRESS = False

        return _EMBEDDINGS_INSTANCE

    def embed_text(self, text):
        """Create embedding for a single text"""
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts):
        """Create embeddings for multiple documents"""
        return self.embeddings.embed_documents(texts)

    def is_loaded(self):
        """Check if embeddings are loaded"""
        return _EMBEDDINGS_INSTANCE is not None


# Create global instance
embedding_service = EmbeddingService()