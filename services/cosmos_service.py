import uuid
from datetime import datetime, timezone

from azure.cosmos import CosmosClient, PartitionKey, exceptions


class CosmosService:
    def __init__(self, endpoint, key, database_name, container_name):
        self._client = CosmosClient(endpoint, credential=key)
        self._database = self._client.create_database_if_not_exists(id=database_name)
        self._container = self._database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/id"),
            offer_throughput=400,
        )

    # ── CREATE ───────────────────────────────────────────────
    def create_item(self, name, description, category, quantity, photo_url="", price=0):
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
        return self._container.create_item(body=item)

    # ── READ (list) ──────────────────────────────────────────
    def get_items(self, search=None, category=None):
        conditions = []
        parameters = []

        if search:
            words = search.lower().split()
            for idx, word in enumerate(words):
                param_name = f"@search{idx}"
                conditions.append(
                    f"(CONTAINS(LOWER(c.name), {param_name}) OR CONTAINS(LOWER(c.description), {param_name}))"
                )
                parameters.append({"name": param_name, "value": word})

        if category:
            conditions.append("c.category = @category")
            parameters.append({"name": "@category", "value": category})

        where_clause = (" WHERE " + " AND ".join(conditions)) if conditions else ""
        query = f"SELECT * FROM c{where_clause} ORDER BY c.created_at DESC"

        return list(
            self._container.query_items(
                query=query,
                parameters=parameters or None,
                enable_cross_partition_query=True,
            )
        )

    # ── READ (single) ───────────────────────────────────────
    def get_item(self, item_id, category=None):
        try:
            return self._container.read_item(item=item_id, partition_key=item_id)
        except exceptions.CosmosResourceNotFoundError:
            return None

    def get_item_by_id(self, item_id):
        """Look up an item by id (direct point-read)."""
        return self.get_item(item_id)

    # ── UPDATE ───────────────────────────────────────────────
    def update_item(self, item_id, category, data):
        item = self.get_item(item_id)
        if not item:
            return None
        for key, value in data.items():
            if key not in ("id", "created_at"):
                item[key] = value
        item["updated_at"] = datetime.now(timezone.utc).isoformat()
        return self._container.replace_item(item=item, body=item)

    # ── DELETE ───────────────────────────────────────────────
    def delete_item(self, item_id, category=None):
        try:
            self._container.delete_item(item=item_id, partition_key=item_id)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False

    # ── CATEGORIES ───────────────────────────────────────────
    def get_categories(self):
        query = "SELECT DISTINCT VALUE c.category FROM c"
        return sorted(
            self._container.query_items(
                query=query, enable_cross_partition_query=True
            )
        )
