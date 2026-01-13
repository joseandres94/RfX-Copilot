from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Response, UploadFile, File
from typing import Annotated
from ....domain.chat_agent.value_objects.consent_method import ConsentMethod
from ....domain.shared.value_objects.session_id import SessionId
from ....domain.shared.entities.deal import DealStatus
from ....domain.shared.repositories.deal_repository import DealRepository
from ....application.chat_agent.use_cases.generate_response_use_case import GenerateResponseUseCase
from ....application.chat_agent.use_cases.save_consent_use_case import SaveConsentUseCase
from ....application.chat_agent.use_cases.speech_use_case import SpeechUseCase
from ....interface.dependencies import get_generate_response_uc
from ....interface.dependencies import get_save_consent_uc
from ....interface.dependencies import get_speech_uc
from ....interface.dependencies import get_deal_repository
from ...schemas.chat_schemas import ChatRequest, ChatResponse
from ...schemas.consent_schemas import ConsentRequest, ConsentResponse
from ...schemas.stt_schemas import STTResponse

import logging
logger = logging.getLogger(__name__)
# Router initialization
router = APIRouter(prefix="", tags=["chat"])

# Health check
@router.get("/health")
def health():
    return{"status": "ok"}

# Chat endpoint
@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    generate_response_uc: Annotated[GenerateResponseUseCase, Depends(get_generate_response_uc)],
    deal_repository: Annotated[DealRepository, Depends(get_deal_repository)]
) -> ChatResponse:
    """
    Handle chat request.
    
    If deal_id is provided, validate that the deal is in READY state before allowing chat.
    The Chat Agent can use deal context (DIC, Demo Brief, Gaps) for RAG responses.
    """
    # Check if text is given
    if not req.text_message:
        raise HTTPException(status_code=400, detail="Text to generate response not found.")

    try:
        # If deal_id provided, validate that it is READY
        if req.deal_id:
            deal = deal_repository.get(req.deal_id)
            
            if not deal:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Deal {req.deal_id} not found"
                )
            
            if deal.status != DealStatus.READY:
                if deal.status == DealStatus.PROCESSING:
                    raise HTTPException(
                        status_code=409,
                        detail=f"The deal is still processing (current step: {deal.current_step.value}). "
                               "Please wait until the pipeline finishes."
                    )
                elif deal.status == DealStatus.ERROR:
                    raise HTTPException(
                        status_code=409,
                        detail=f"The deal encountered an error: {deal.error_message}"
                    )
            
            logger.info(f"Chat request for deal {req.deal_id} (status: {deal.status.value})")
        
        # Generate response
        session_id = SessionId(req.session_id)
        response = await generate_response_uc.execute(session_id, deal, req.text_message, req.language)
        return ChatResponse(answer=response.content, stage=response.stage)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to generate response: {e}")

# Save consent
@router.post("/consent")
def save_consent(
    cons: ConsentRequest,
    save_consent_uc: Annotated[SaveConsentUseCase, Depends(get_save_consent_uc)]
) -> ConsentResponse:
    """Save consent"""
    try:
        # Save consent
        success = save_consent_uc.execute(
            patient_name=cons.patient_name,
            session_id=SessionId(cons.session_id),
            method=ConsentMethod(cons.method),
            timestamp=datetime.now(timezone.utc)
        )
        return ConsentResponse(success=success)
    except Exception as e:
        logger.error(f"Error in save consent endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to save consent: {e}")

# Speech-to-text (Transcribe audio)
@router.post("/stt", response_model=STTResponse)
async def stt(
    speech_uc: Annotated[SpeechUseCase, Depends(get_speech_uc)],
    file: UploadFile = File(...)
) -> STTResponse:
    """Transcribe audio to text"""
    try:
        # Get transcription
        audio_data = await file.read()
        transcription = speech_uc.execute_stt(audio_data, file.filename)
        return STTResponse(transcription=transcription)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in STT endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to transcribe audio: {e}")

# Text-to-speech (TTS)
@router.post("/tts")
def tts(
    req: ChatRequest,
    speech_uc: Annotated[SpeechUseCase, Depends(get_speech_uc)]
) -> Response:
    """Generate voice from text"""
    # Check if text is given
    if not req.text_message:
        raise HTTPException(status_code=400, detail="Text to generate voice not found.")

    try:
        # Generate voice from text
        logger.info(f"Generating voice from text: {req.text_message}")
        audio = speech_uc.execute_tts(text_message=req.text_message, language=req.language)
        logger.info(f"Voice generated successfully with type: {type(audio)}")
        return Response(audio, media_type="audio/wav")

    except Exception as e:
        logger.error(f"Error in TTS endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to generate voice.")