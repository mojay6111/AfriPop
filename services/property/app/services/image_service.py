import io
import uuid
from PIL import Image
import imagehash
from minio import Minio
from minio.error import S3Error
from app.config import settings

client = Minio(
    f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=False,
)


def ensure_bucket():
    if not client.bucket_exists(settings.MINIO_BUCKET):
        client.make_bucket(settings.MINIO_BUCKET)


def process_and_upload(file_bytes: bytes, original_filename: str) -> dict:
    ensure_bucket()
    img = Image.open(io.BytesIO(file_bytes))

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    max_width = 1200
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)

    width, height = img.size
    phash = str(imagehash.phash(img))

    output = io.BytesIO()
    img.save(output, format="JPEG", quality=85, optimize=True)
    output.seek(0)
    file_size = output.getbuffer().nbytes

    filename = f"{uuid.uuid4()}.jpg"
    client.put_object(
        settings.MINIO_BUCKET,
        filename,
        output,
        length=file_size,
        content_type="image/jpeg",
    )

    url = f"http://{settings.MINIO_HOST}:{settings.MINIO_PORT}/{settings.MINIO_BUCKET}/{filename}"

    return {
        "url": url,
        "filename": filename,
        "file_size": file_size,
        "width": width,
        "height": height,
        "phash": phash,
    }


def delete_image(filename: str):
    try:
        client.remove_object(settings.MINIO_BUCKET, filename)
    except S3Error as e:
        print(f"MinIO delete error: {e}")
