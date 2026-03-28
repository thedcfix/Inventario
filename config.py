import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

    # Authentication
    APP_USERNAME = os.environ.get("APP_USERNAME", "admin")
    APP_PASSWORD_HASH = os.environ.get("APP_PASSWORD_HASH", "")

    # Azure Cosmos DB
    COSMOS_ENDPOINT = os.environ.get("COSMOS_ENDPOINT", "")
    COSMOS_KEY = os.environ.get("COSMOS_KEY", "")
    COSMOS_DATABASE = os.environ.get("COSMOS_DATABASE", "inventario")
    COSMOS_CONTAINER = os.environ.get("COSMOS_CONTAINER", "items")

    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get(
        "AZURE_STORAGE_CONNECTION_STRING", ""
    )
    AZURE_STORAGE_CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER", "photos")
