from twilio.rest import Client
from core.config import settings

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
twilio_whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER

twilio_client = Client(account_sid, auth_token)

def send_message_via_twilio_sms(body, to):
    twilio_client.messages.create(
        body=body, 
        from_=twilio_whatsapp_number,
        to=to
    )

def new_send_whatsapp_template_via_twilio(content_sid, to, content_variables=None):
    try:
        message_params = {
            "from_": "whatsapp:" + twilio_whatsapp_number.strip(),
            "to": "whatsapp:" + to.strip(),
            "content_sid": content_sid
        }
        if content_variables:
            message_params["content_variables"] = content_variables  # Should be a JSON string
        twilio_client.messages.create(**message_params)
    except Exception as e:
        print("Failed to send WhatsApp template message via Twilio:", e)

def send_message_via_twilio_with_media(body, to, media_url=None):
    print("Sending message via twilio")
    print("Body: ", body)
    print("To: ", to)
    print("Media URL: ", media_url)
    print("Twilio Whatsapp Number: ", twilio_whatsapp_number)
    try:
        message_params = {
            "body": body,
            "from_": "whatsapp:" + twilio_whatsapp_number.strip(),
            "to": "whatsapp:" + to.strip()
        }
        if media_url:
            message_params["media_url"] = [media_url]
            
        twilio_client.messages.create(**message_params)
    except Exception as e:
        print("Failed to send message via twilio", e)

def send_message_via_twilio(body, to):
    print("Sending message via twilio")
    print("Body: ", body)
    print("To: ", to)
    print("Twilio Whatsapp Number: ", twilio_whatsapp_number)
    try:
        message_params = {
            "body": body,
            "from_": "whatsapp:" + twilio_whatsapp_number.strip(),
            "to": "whatsapp:" + to.strip()
        }
        twilio_client.messages.create(**message_params)
    except Exception as e:
        print("Failed to send message via twilio", e)
