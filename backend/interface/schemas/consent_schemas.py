from pydantic import BaseModel, Field


# Classes definition
class ConsentRequest(BaseModel):
    """Request schema for the consent"""
    patient_name: str = Field(..., description="The patient name")
    session_id: str = Field(..., description="The session ID")
    method: str = Field(..., description="The consent method")


class ConsentResponse(BaseModel):
    """Response schema for the consent"""
    success: bool = Field(..., description="Success status")