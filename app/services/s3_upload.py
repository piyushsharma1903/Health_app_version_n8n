import uuid
from io import BytesIO
import boto3
from app.config import settings

s3 = boto3.client(
    "s3",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET
)

def upload_image_to_s3(image_bytes: bytes, content_type: str):
    key = f"reports/{uuid.uuid4()}.png"

    s3.upload_fileobj(
        BytesIO(image_bytes),
        settings.S3_BUCKET,
        key,
        ExtraArgs={
            "ContentType": content_type
            # DO NOT PUT ACL HERE — your bucket has ACLs disabled
        }
    )

    return f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
