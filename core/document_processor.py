import uuid
from pathlib import Path
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from config import Config


class DocumentProcessor:
    """Document processing with OCR - CLEANED & FIXED VERSION"""

    def __init__(self):
        self.allowed_extensions = Config.ALLOWED_EXTENSIONS
        self.max_file_size = Config.MAX_FILE_SIZE

    def is_allowed_file(self, filename):
        """Check if file extension is allowed"""
        return Path(filename).suffix.lower() in self.allowed_extensions

    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text() + "\n"
            doc.close()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def extract_text_from_image(self, file_path):
        """Extract text from image using Tesseract OCR"""
        try:
            # Configure Tesseract for German and English
            custom_config = r'--oem 3 --psm 6 -l deu+eng'

            # Open and process image
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, config=custom_config)
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")

    def process_document(self, file_path):
        """Main method to process any document"""
        file_extension = Path(file_path).suffix.lower()

        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.png', '.jpg', '.jpeg']:
            return self.extract_text_from_image(file_path)
        else:
            raise Exception(f"Unsupported file type: {file_extension}")

    def save_uploaded_file(self, file):
        """Save uploaded file and return path - FIXED VERSION"""
        if not file or file.filename == '':
            raise Exception("No file selected")

        if not self.is_allowed_file(file.filename):
            raise Exception(f"File type not allowed. Allowed: {', '.join(self.allowed_extensions)}")

        # Create unique filename
        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = Config.UPLOADS_DIR / unique_filename

        try:
            # Save file
            file.save(file_path)

            # Check file size AFTER saving (more reliable)
            if file_path.stat().st_size > self.max_file_size:
                file_path.unlink()  # Delete the file
                max_mb = self.max_file_size // (1024 * 1024)
                raise Exception(f"File too large. Maximum size: {max_mb}MB")

            return file_path

        except Exception as e:
            # Clean up file if it exists
            if file_path.exists():
                file_path.unlink()
            raise Exception(f"Error saving file: {str(e)}")


# Create global instance
document_processor = DocumentProcessor()