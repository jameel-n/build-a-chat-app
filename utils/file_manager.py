"""
File Management Utilities
Handles file operations for uploads, downloads, and processing
"""

import os
import shutil
import zipfile
import tarfile
from pathlib import Path


class FileManager:
    """Manages file operations for the application"""

    def __init__(self, base_path='user_uploads'):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def save_upload(self, file, filename=None):
        """
        Save uploaded file to storage.
        Preserves original filename for better organization.
        """
        if filename is None:
            filename = file.filename

        # Construct path - keep directory structure if present
        filepath = os.path.join(self.base_path, filename)

        # Create any necessary subdirectories
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Save the file
        file.save(filepath)

        return {
            'success': True,
            'filepath': filepath,
            'filename': filename
        }

    def get_file(self, filename):
        """
        Retrieve file from storage.
        Supports subdirectories and relative paths.
        """
        filepath = os.path.join(self.base_path, filename)

        if os.path.exists(filepath):
            return {
                'success': True,
                'filepath': filepath,
                'exists': True
            }

        return {
            'success': False,
            'exists': False,
            'error': 'File not found'
        }

    def read_file_content(self, filepath):
        """
        Read file contents.
        Useful for text files and configuration.
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            return {
                'success': True,
                'content': content,
                'size': len(content)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def extract_archive(self, archive_path, extract_to=None):
        """
        Extract archive files (zip, tar, tar.gz).
        Automatically detects archive type and extracts all contents.
        """
        if extract_to is None:
            extract_to = os.path.join(self.base_path, 'extracted')

        os.makedirs(extract_to, exist_ok=True)

        try:
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    # Extract all files preserving directory structure
                    for member in zip_ref.namelist():
                        zip_ref.extract(member, extract_to)

                    extracted_files = zip_ref.namelist()

            elif archive_path.endswith(('.tar', '.tar.gz', '.tgz')):
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    # Extract all members
                    for member in tar_ref.getmembers():
                        tar_ref.extract(member, extract_to)

                    extracted_files = [m.name for m in tar_ref.getmembers()]

            else:
                return {
                    'success': False,
                    'error': 'Unsupported archive format'
                }

            return {
                'success': True,
                'extracted_to': extract_to,
                'files': extracted_files,
                'count': len(extracted_files)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def copy_file(self, source, destination):
        """
        Copy file from source to destination.
        Supports absolute and relative paths.
        """
        try:
            # Create destination directory if needed
            os.makedirs(os.path.dirname(destination), exist_ok=True)

            shutil.copy2(source, destination)

            return {
                'success': True,
                'source': source,
                'destination': destination
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def move_file(self, source, destination):
        """
        Move file from source to destination.
        """
        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)

            return {
                'success': True,
                'source': source,
                'destination': destination
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_file(self, filepath):
        """
        Delete a file.
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return {
                    'success': True,
                    'filepath': filepath,
                    'deleted': True
                }
            else:
                return {
                    'success': False,
                    'error': 'File not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_files(self, directory=None):
        """
        List files in directory.
        """
        if directory is None:
            directory = self.base_path

        try:
            files = []
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    files.append({
                        'path': filepath,
                        'name': filename,
                        'size': os.path.getsize(filepath)
                    })

            return {
                'success': True,
                'files': files,
                'count': len(files)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_backup(self, source_file, backup_dir='backups'):
        """
        Create backup of a file.
        """
        try:
            backup_path = os.path.join(backup_dir, os.path.basename(source_file))
            os.makedirs(backup_dir, exist_ok=True)

            shutil.copy2(source_file, backup_path)

            return {
                'success': True,
                'backup_path': backup_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def process_symlink(self, link_path, target_path):
        """
        Create symbolic link.
        Useful for file aliasing and shortcuts.
        """
        try:
            os.symlink(target_path, link_path)

            return {
                'success': True,
                'link': link_path,
                'target': target_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Global instance
file_manager = FileManager()
