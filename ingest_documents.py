#!/usr/bin/env python3
"""
Script to ingest PDF documents into the knowledge base with resume capability
"""

import json
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime
from services.vector_store import vector_store
from utils.text_processing import text_processor


class DocumentIngester:
    def __init__(self):
        self.docs_dir = Path("data/knowledge_base/documents")
        self.chunks_dir = Path("data/knowledge_base/chunks")
        self.progress_file = Path("data/knowledge_base/ingestion_progress.json")

        # Create directories
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.chunks_dir.mkdir(parents=True, exist_ok=True)

        # Load progress
        self.progress = self._load_progress()

    def _load_progress(self):
        """Load ingestion progress from file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'processed_files': {},
            'last_run': None,
            'total_chunks': 0
        }

    def _save_progress(self):
        """Save ingestion progress to file"""
        self.progress['last_run'] = datetime.now().isoformat()
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)

    def _is_file_processed(self, pdf_path):
        """Check if file was already processed"""
        file_key = pdf_path.name
        if file_key not in self.progress['processed_files']:
            return False

        # Check if file was modified since last processing
        stored_mtime = self.progress['processed_files'][file_key].get('modified_time')
        current_mtime = pdf_path.stat().st_mtime

        return stored_mtime == current_mtime

    def _mark_file_processed(self, pdf_path, chunks_count):
        """Mark file as processed"""
        file_key = pdf_path.name
        self.progress['processed_files'][file_key] = {
            'modified_time': pdf_path.stat().st_mtime,
            'chunks_count': chunks_count,
            'processed_at': datetime.now().isoformat()
        }
        self.progress['total_chunks'] += chunks_count

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            doc = fitz.open(pdf_path)
            pages_text = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text.strip():
                    pages_text.append({
                        'page_number': page_num + 1,
                        'text': page_text.strip()
                    })
            doc.close()
            return pages_text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return None

    def save_chunks_as_jsonl(self, chunks, pdf_path):
        """Save chunks in JSONL format"""
        jsonl_file = self.chunks_dir / f"{pdf_path.stem}_chunks.jsonl"

        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                json.dump(chunk, f, ensure_ascii=False)
                f.write('\n')

        return jsonl_file

    def load_chunks_from_jsonl(self, jsonl_file):
        """Load chunks from JSONL file"""
        chunks = []
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
        return chunks

    def process_single_pdf(self, pdf_path, force=False):
        """Process a single PDF file"""

        # Check if already processed
        if not force and self._is_file_processed(pdf_path):
            stored_info = self.progress['processed_files'][pdf_path.name]
            print(f"  ⏭️  Skipping {pdf_path.name} (already processed, {stored_info['chunks_count']} chunks)")
            return stored_info['chunks_count']

        print(f"Processing: {pdf_path.name}")

        # Extract text with page information
        pages_data = self.extract_text_from_pdf(pdf_path)

        if not pages_data:
            print(f"  ❌ Failed to extract text from {pdf_path.name}")
            return 0

        # Combine all pages
        full_text = "\n\n".join([page['text'] for page in pages_data])

        # Clean the text
        cleaned_text = text_processor.clean_text(full_text)

        if not cleaned_text.strip():
            print(f"  ❌ No readable text found in {pdf_path.name}")
            return 0

        # Create base metadata
        base_metadata = {
            'source': pdf_path.name,
            'file_path': str(pdf_path),
            'document_type': 'official_document',
            'language': 'de',
            'total_pages': len(pages_data),
            'processed_at': datetime.now().isoformat()
        }

        # Split into chunks and create detailed metadata
        text_splitter = vector_store.text_splitter
        text_chunks = text_splitter.split_text(cleaned_text)

        detailed_chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                'chunk_id': i,
                'chunk_index': f"{pdf_path.stem}_{i:03d}",
                'chunk_size': len(chunk_text)
            })

            detailed_chunks.append({
                'content': chunk_text,
                'metadata': chunk_metadata
            })

        # Save chunks as JSONL
        jsonl_file = self.save_chunks_as_jsonl(detailed_chunks, pdf_path)
        print(f"  💾 Saved {len(detailed_chunks)} chunks to {jsonl_file.name}")

        # Add to vector store
        chunks_added = vector_store.add_document(cleaned_text, base_metadata)

        # Mark as processed
        self._mark_file_processed(pdf_path, chunks_added)

        print(f"  ✅ Added {chunks_added} chunks to vector store")
        return chunks_added

    def process_all_pdfs(self, force=False):
        """Process all PDFs in the documents directory"""

        pdf_files = list(self.docs_dir.glob("*.pdf"))

        if not pdf_files:
            print(f"No PDF files found in {self.docs_dir}")
            print("Please add your German bureaucracy PDFs to this directory and run again.")
            return

        print(f"Found {len(pdf_files)} PDF files")
        if not force:
            already_processed = sum(1 for pdf in pdf_files if self._is_file_processed(pdf))
            print(f"Already processed: {already_processed}")
            print(f"To process: {len(pdf_files) - already_processed}")

        total_new_chunks = 0

        for pdf_path in pdf_files:
            try:
                chunks_added = self.process_single_pdf(pdf_path, force)
                total_new_chunks += chunks_added

                # Save progress after each file
                self._save_progress()

            except KeyboardInterrupt:
                print(f"\n⏸️  Processing interrupted. Progress saved.")
                print(f"   Run again to resume from where you left off.")
                self._save_progress()
                return
            except Exception as e:
                print(f"  ❌ Error processing {pdf_path.name}: {e}")
                continue

        # Final summary
        info = vector_store.get_collection_info()

        print(f"\n🎉 Processing complete!")
        print(f"PDFs processed: {len(pdf_files)}")
        print(f"New chunks added this run: {total_new_chunks}")
        print(f"Total chunks in vector DB: {info['count']}")

        self._save_progress()
        self._test_knowledge_base()

    def _test_knowledge_base(self):
        """Test the knowledge base with sample queries"""
        print(f"\n🔍 Testing knowledge base...")
        test_queries = [
            "Bürgergeld",
            "Antrag",
            "Jobcenter",
            "Dokumente",
            "Bedarfsgemeinschaft"
        ]

        for query in test_queries:
            results = vector_store.search(query, k=2)
            print(f"  Query '{query}': Found {len(results)} results")
            if results and results[0].page_content:
                snippet = results[0].page_content[:80].replace('\n', ' ')
                print(f"    Best match: {snippet}...")

    def list_documents(self):
        """List all documents and their status"""
        pdf_files = list(self.docs_dir.glob("*.pdf"))

        print(f"Documents in {self.docs_dir}:")
        if pdf_files:
            for pdf in pdf_files:
                status = "✅ Processed" if self._is_file_processed(pdf) else "⏳ Pending"
                if pdf.name in self.progress['processed_files']:
                    chunks = self.progress['processed_files'][pdf.name]['chunks_count']
                    print(f"  📄 {pdf.name} - {status} ({chunks} chunks)")
                else:
                    print(f"  📄 {pdf.name} - {status}")
        else:
            print("  No PDF files found")

        # Show vector store info
        info = vector_store.get_collection_info()
        print(f"\nVector database status:")
        print(f"  Total chunks: {info['count']}")
        print(f"  Last run: {self.progress.get('last_run', 'Never')}")

    def reset_progress(self):
        """Reset all progress (use with caution)"""
        if self.progress_file.exists():
            self.progress_file.unlink()

        # Clear chunks directory
        for jsonl_file in self.chunks_dir.glob("*.jsonl"):
            jsonl_file.unlink()

        print("Progress reset. All files will be reprocessed on next run.")


def main():
    import sys

    ingester = DocumentIngester()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "list":
            ingester.list_documents()
        elif command == "reset":
            ingester.reset_progress()
        elif command == "force":
            print("Force processing all files...")
            ingester.process_all_pdfs(force=True)
        else:
            print("Usage: python ingest_documents.py [list|reset|force]")
    else:
        ingester.process_all_pdfs()


if __name__ == "__main__":
    main()