import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from werkzeug.utils import secure_filename
from config import Config


class FileUtils:
    """Utility class for file operations"""

    @staticmethod
    def get_file_hash(file_path: Path) -> str:
        """Generate hash for file to detect duplicates"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        """Check if file extension is allowed"""
        if not filename:
            return False

        file_ext = Path(filename).suffix.lower()
        return file_ext in Config.ALLOWED_EXTENSIONS

    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """Generate safe filename"""
        if not filename:
            return "unknown_file"

        # Use werkzeug's secure_filename and preserve extension
        safe_name = secure_filename(filename)
        if not safe_name:
            # If secure_filename returns empty, create a generic name
            ext = Path(filename).suffix.lower()
            safe_name = f"uploaded_file{ext}"

        return safe_name

    @staticmethod
    def ensure_directory(directory: Path) -> bool:
        """Ensure directory exists, create if not"""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            return False

    @staticmethod
    def cleanup_old_files(directory: Path, max_age_hours: int = 24) -> int:
        """Clean up old files in directory"""
        if not directory.exists():
            return 0

        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0

        try:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
        except Exception as e:
            print(f"Error cleaning up files: {e}")

        return deleted_count

    @staticmethod
    def get_file_info(file_path: Path) -> Dict:
        """Get comprehensive file information"""
        if not file_path.exists():
            return {}

        stat = file_path.stat()
        return {
            'name': file_path.name,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'extension': file_path.suffix.lower(),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'is_allowed': FileUtils.is_allowed_file(file_path.name),
            'hash': FileUtils.get_file_hash(file_path)
        }

    @staticmethod
    def list_files_by_type(directory: Path, extensions: List[str] = None) -> List[Dict]:
        """List files in directory with their info"""
        if not directory.exists():
            return []

        if extensions is None:
            extensions = list(Config.ALLOWED_EXTENSIONS)

        files_info = []
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                files_info.append(FileUtils.get_file_info(file_path))

        return sorted(files_info, key=lambda x: x.get('modified', 0), reverse=True)

    @staticmethod
    def validate_file_size(file_path: Path, max_size: int = None) -> tuple[bool, str]:
        """Validate file size"""
        if max_size is None:
            max_size = Config.MAX_FILE_SIZE

        if not file_path.exists():
            return False, "File does not exist"

        file_size = file_path.stat().st_size
        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            return False, f"File too large. Maximum size is {max_mb:.1f}MB"

        return True, "File size is valid"


# Create global instance
file_utils = FileUtils()