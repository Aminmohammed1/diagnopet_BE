import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from utils.supabase_storage import upload_pdf, get_signed_url
from utils.send_whatsapp_msg import send_message_via_twilio_with_media

load_dotenv()

def test_flow():
    # 1. Test Supabase Upload
    print("Testing Supabase Upload...")
    test_content = b"%PDF-1.4 test content"
    test_filename = "test_report.pdf"
    try:
        res = upload_pdf(test_content, test_filename)
        print(f"Upload successful: {res}")
    except Exception as e:
        print(f"Upload failed: {e}")
        return

    # 2. Test Signed URL Generation
    print("\nTesting Signed URL Generation...")
    try:
        signed_url = get_signed_url(test_filename, expires_in=60)
        print(f"Signed URL: {signed_url}")
    except Exception as e:
        print(f"Signed URL generation failed: {e}")
        return

    # 3. Test WhatsApp Sending (Optional: requires valid phone number)
    phone_number = os.getenv("TEST_PHONE_NUMBER")
    if phone_number:
        print(f"\nTesting WhatsApp Sending to {phone_number}...")
        try:
            send_message_via_twilio_with_media(
                "Test PDF delivery",
                phone_number,
                media_url=signed_url
            )
            print("WhatsApp message sent successfully")
        except Exception as e:
            print(f"WhatsApp sending failed: {e}")
    else:
        print("\nSkipping WhatsApp test (TEST_PHONE_NUMBER not set in .env)")

if __name__ == "__main__":
    test_flow()
