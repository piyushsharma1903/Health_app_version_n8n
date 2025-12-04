import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB = os.getenv("MONGO_DB")
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

    AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
    AZURE_KEY = os.getenv("AZURE_KEY")

    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    S3_BUCKET = os.getenv("S3_BUCKET_NAME")
    N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
settings = Settings()
