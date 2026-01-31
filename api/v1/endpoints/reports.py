from fastapi import APIRouter, UploadFile, Form, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from utils.supabase_storage import upload_pdf, get_signed_url
from utils.send_whatsapp_msg import send_message_via_twilio_with_media
import uuid
from crud import crud_order
from schemas.order import OrderCreate
router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


from api.deps import get_current_admin_or_staff_user
from db.models.user import User

@router.post("/upload-report")
async def upload_report(
    # user_id: int = Form(...),
    appointment_id: int = Form(...),
    booking_item_id: int = Form(...),
    phone_number: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_or_staff_user),
    db: AsyncSession = Depends(get_db)
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
            f"phonenumber_{phone_number}/"
            f"appointment_{appointment_id}/"
            f"report_{booking_item_id}.pdf"
        )
        
        # 3. Upload to Supabase
        upload_pdf(file_content=content, storage_path=storage_path, content_type="application/pdf")
        
        # 4. Generate signed URL (short expiry, e.g., 1 hour)
        signed_url = get_signed_url(storage_path, expires_in=3600)

        order_crud = crud_order.CrudOrder(db)
        await order_crud.create_order(
            OrderCreate(
                user_id=current_user.id,
                booking_id=appointment_id,
                booking_item_id=booking_item_id,
                file_link=signed_url
            )
        )
        
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


from api.deps import get_current_user
from utils.supabase_storage import list_files

@router.get("/")
async def get_user_reports(
    current_user: User = Depends(get_current_user)
):
    """
    List all reports for the current user.
    """
    try:
        user_folder = f"user_{current_user.id}"
        
        # 1. List appointments folders
        appointments = list_files(user_folder)
        
        reports = []
        
        if appointments:
            for appt in appointments:
                appt_folder_name = appt['name']
                # Expecting format appointment_{id}
                if not appt_folder_name.startswith("appointment_"):
                    continue
                
                appt_path = f"{user_folder}/{appt_folder_name}"
                
                # 2. List files in appointment folder
                files = list_files(appt_path)
                
                if files:
                    for file in files:
                        file_name = file['name']
                        if file_name.endswith(".pdf"):
                            file_path = f"{appt_path}/{file_name}"
                            
                            # 3. Generate signed URL
                            signed_url = get_signed_url(file_path, expires_in=3600)
                            
                            reports.append({
                                "filename": file_name,
                                "path": file_path,
                                "url": signed_url,
                                "created_at": file.get("created_at"), # Supabase returns metadata
                                "appointment_id": appt_folder_name.split("_")[1]
                            })
                            
        return reports

    except Exception as e:
        print(f"Error in get_user_reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# @router.get("/download-report")        
