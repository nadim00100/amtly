from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from services.embedding_service import embedding_service
from config import Config


class VectorStore:
    """Vector store for knowledge base - CLEANED VERSION"""

    def __init__(self):
        self.embeddings = embedding_service.embeddings
        self.persist_directory = Config.KNOWLEDGE_BASE_DIR / "embeddings"
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize Chroma
        self.vectorstore = Chroma(
            persist_directory=str(self.persist_directory),
            embedding_function=self.embeddings,
            collection_name="amtly_knowledge"
        )

        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def add_document(self, text, metadata=None):
        """Add a single document to the vector store"""
        if metadata is None:
            metadata = {}

        # Split text into chunks
        chunks = self.text_splitter.split_text(text)

        # Create Document objects
        documents = []
        for i, chunk in enumerate(chunks):
            doc_metadata = metadata.copy()
            doc_metadata['chunk_id'] = i
            documents.append(Document(page_content=chunk, metadata=doc_metadata))

        # Add to vector store
        try:
            self.vectorstore.add_documents(documents)
            return len(documents)
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            return 0

    def search(self, query, k=5, filter=None):
        """Search for similar documents"""
        try:
            results = self.vectorstore.similarity_search(
                query,
                k=k,
                filter=filter
            )
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def search_with_scores(self, query, k=5, filter=None):
        """Search with similarity scores"""
        try:
            results = self.vectorstore.similarity_search_with_score(
                query,
                k=k,
                filter=filter
            )
            return results
        except Exception as e:
            print(f"Search with scores error: {e}")
            return []

    def get_collection_info(self):
        """Get information about the collection"""
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            return {
                'count': count,
                'name': collection.name,
                'status': 'ready' if count > 0 else 'empty'
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {'count': 0, 'name': 'unknown', 'status': 'error'}


# Create global instance
vector_store = VectorStore()