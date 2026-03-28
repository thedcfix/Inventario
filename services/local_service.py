"""
In-memory fallback services for local development without Azure.
Data is stored in a JSON file; photos are saved to static/uploads/.
"""

import json
import os
import shutil
import uuid
from datetime import datetime, timezone


DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "items.json")
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")


def _ensure_dirs():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def _load():
    _ensure_dirs()
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def _save(items):
    _ensure_dirs()
    with open(DATA_FILE, "w") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


class LocalCosmosService:
    """Drop-in replacement for CosmosService using a local JSON file."""

    def __init__(self, **_kwargs):
        _ensure_dirs()

    def create_item(self, name, description, category, quantity, photo_url="", price=0):
        items = _load()
        item = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "category": category,
            "quantity": int(quantity),
            "price": float(price),
            "photo_url": photo_url,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        items.append(item)
        _save(items)
        return item

    def get_items(self, search=None, category=None):
        items = _load()
        if search:
            words = search.lower().split()
            items = [
                i for i in items
                if all(
                    w in i.get("name", "").lower() or w in i.get("description", "").lower()
                    for w in words
                )
            ]
        if category:
            items = [i for i in items if i.get("category") == category]
        return sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)

    def get_item(self, item_id, category):
        items = _load()
        for i in items:
            if i["id"] == item_id and i["category"] == category:
                return i
        return None

    def get_item_by_id(self, item_id):
        items = _load()
        for i in items:
            if i["id"] == item_id:
                return i
        return None

    def update_item(self, item_id, category, data):
        items = _load()
        for i in items:
            if i["id"] == item_id:
                for key, value in data.items():
                    if key not in ("id", "created_at"):
                        i[key] = value
                i["updated_at"] = datetime.now(timezone.utc).isoformat()
                _save(items)
                return i
        return None

    def delete_item(self, item_id, category):
        items = _load()
        new_items = [i for i in items if i["id"] != item_id]
        if len(new_items) < len(items):
            _save(new_items)
            return True
        return False

    def get_categories(self):
        items = _load()
        return sorted(set(i.get("category", "") for i in items if i.get("category")))


class LocalStorageService:
    """Drop-in replacement for StorageService using local filesystem."""

    def __init__(self, **_kwargs):
        _ensure_dirs()

    def upload_photo(self, file_stream, original_filename):
        ext = os.path.splitext(original_filename)[1].lower() or ".jpg"
        blob_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, blob_name)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file_stream, f)
        photo_url = f"/static/uploads/{blob_name}"
        return blob_name, photo_url

    def delete_photo(self, blob_name):
        if not blob_name:
            return
        filepath = os.path.join(UPLOAD_DIR, blob_name)
        if os.path.exists(filepath):
            os.remove(filepath)
