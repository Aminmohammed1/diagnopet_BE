from pydantic import BaseModel

class VerifyOtpRequest(BaseModel):
    phone: str
    otp_code: str