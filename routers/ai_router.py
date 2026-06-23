from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session
from database import get_session
from typing import Optional
from schemas.ai_schemas import AIOrderResponse
from services.ai_service import parse_order_with_ai

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/parse-order", response_model=AIOrderResponse)
async def parse_order(
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session)
):
    try:
        return await parse_order_with_ai(session=session, text=text, audio=audio)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")
