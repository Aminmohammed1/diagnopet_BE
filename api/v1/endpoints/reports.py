from fastapi import APIRouter, UploadFile, Form, File, HTTPException, Depends
from utils.supabase_storage import upload_pdf, get_signed_url
from utils.send_whatsapp_msg import send_message_via_twilio_with_media
import uuid

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload-report")
async def upload_report(
    user_id: int = Form(...),
    appointment_id: int = Form(...),
    phone_number: str = Form(...),
    file: UploadFile = File(...)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # 1. Read file content
        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="PDF too large")
        
        # 2. Generate unique filename
        # file_extension = file.filename.split(".")[-1]
        # date = datetime.now().strftime("%Y-%m-%d")
        # user_id = user_id
        # appointment_id = appointment_id
        # unique_filename = f"{date}_{user_id}_{appointment_id}_{uuid.uuid4()}.{file_extension}"

        # 2. Generate unique filename
        file_id = str(uuid.uuid4())
        storage_path = (
            f"user_{user_id}/"
            f"appointment_{appointment_id}/"
            f"report_{file_id}.pdf"
        )
        
        # 3. Upload to Supabase
        upload_pdf(file_content=content, storage_path=storage_path, content_type="application/pdf")
        
        # 4. Generate signed URL (short expiry, e.g., 1 hour)
        signed_url = get_signed_url(storage_path, expires_in=3600)
        
        # 5. Send via WhatsApp
        message_body = "Your medical report is ready. Please find it attached below."
        send_message_via_twilio_with_media(message_body, phone_number, media_url=signed_url)
        
        return {
            "message": "Report uploaded and sent successfully",
            "filename": storage_path,
            "signed_url": signed_url
        }
    except Exception as e:
        print(f"Error in upload_report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
