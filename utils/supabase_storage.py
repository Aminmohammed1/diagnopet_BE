from supabase import create_client, Client
from core.config import settings
import io

supabase_url = settings.SUPABASE_URL
supabase_key = settings.SUPABASE_KEY
supabase_bucket = settings.SUPABASE_BUCKET

supabase: Client = create_client(supabase_url, supabase_key)

def upload_pdf(file_content: bytes, storage_path: str, content_type: str = "application/pdf"):
    """
    Uploads a PDF to Supabase Storage.
    """
    try:
        res = supabase.storage.from_(supabase_bucket).upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": content_type, "upsert": False}
        )
        return res
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        raise e

def get_signed_url(file_path: str, expires_in: int = 3600):
    """
    Generates a temporary signed URL for a file in Supabase Storage.
    """
    try:
        res = supabase.storage.from_(supabase_bucket).create_signed_url(
            path=file_path,
            expires_in=expires_in
        )
        return res['signedURL']
    except Exception as e:
        print(f"Error generating signed URL: {e}")
        raise e
