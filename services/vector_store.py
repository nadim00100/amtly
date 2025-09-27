import os
import json
from pathlib import Path
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from services.embedding_service import embedding_service
from config import Config


class VectorStore:
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

    def add_documents_from_directory(self, directory_path):
        """Add all documents from a directory"""
        directory = Path(directory_path)
        added_count = 0

        for file_path in directory.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                metadata = {
                    'source': file_path.name,
                    'file_path': str(file_path),
                    'document_type': 'knowledge_base'
                }

                count = self.add_document(content, metadata)
                added_count += count
                print(f"Added {count} chunks from {file_path.name}")

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        return added_count

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

    def load_chunks_from_jsonl(self, jsonl_file):
        """Load and inspect chunks from JSONL file"""
        chunks = []
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        chunks.append(json.loads(line))
        except Exception as e:
            print(f"Error loading JSONL file {jsonl_file}: {e}")
        return chunks

    def get_chunk_files(self):
        """List all JSONL chunk files"""
        chunks_dir = Config.KNOWLEDGE_BASE_DIR / "chunks"
        if chunks_dir.exists():
            return list(chunks_dir.glob("*.jsonl"))
        return []

    def test_search(self, query="test", k=3):
        """Test search functionality"""
        try:
            results = self.search_with_scores(query, k=k)
            return {
                'query': query,
                'results_count': len(results),
                'results': [
                    {
                        'content': doc.page_content[:200] + "...",
                        'score': float(score),
                        'source': doc.metadata.get('source', 'unknown')
                    }
                    for doc, score in results
                ]
            }
        except Exception as e:
            return {'error': str(e), 'results_count': 0}


# Create global instance
vector_store = VectorStore()