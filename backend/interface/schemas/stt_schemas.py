from pydantic import BaseModel, Field


class STTResponse(BaseModel):
    """Response schema for transcribing audio to text"""
    transcription: str = Field(..., description="Transcription of the audio")