import json
import os
from datetime import datetime

class DataMerger:
    @staticmethod
    def save_to_file(data, filename="combined.json"):
        os.makedirs("../../data/processed", exist_ok=True)
        filepath = f"../../data/processed/{filename}"
        
        existing = []
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                existing = json.load(f)
        
        existing.append(data)
        
        with open(filepath, "w") as f:
            json.dump(existing, f, indent=2)