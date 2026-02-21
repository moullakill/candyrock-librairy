import os
import hashlib

class FileManager:
    def __init__(self, target_path):
        self.target_path = target_path
        if not os.path.exists(self.target_path):
            os.makedirs(self.target_path)

    def calculate_sha1(self, filename):
        path = os.path.join(self.target_path, filename)
        if not os.path.exists(path):
            return None
        sha1 = hashlib.sha1()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest()

    def remove_file(self, filename):
        path = os.path.join(self.target_path, filename)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def list_files(self, extension=None):
        """Liste les fichiers, optionnellement filtrés par extension."""
        if extension:
            return [f for f in os.listdir(self.target_path) if f.endswith(extension)]
        return os.listdir(self.target_path)