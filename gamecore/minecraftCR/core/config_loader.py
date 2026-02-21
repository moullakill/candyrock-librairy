import json
import os
 
class ConfigLoader:
    def __init__(self, filepath):
        self.filepath = filepath

    def load(self):
        if not os.path.exists(self.filepath):
            return None
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self, data):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def update_hash(self, mod_name, sha1_hash):
        data = self.load() or {}
        if "hashes" not in data:
            data["hashes"] = {}
        data["hashes"][mod_name] = sha1_hash
        self.save(data)