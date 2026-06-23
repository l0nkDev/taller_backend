import os
import json
import tempfile
import time
from typing import Optional
from fastapi import UploadFile
from google import genai
from google.genai import types
from schemas.ai_schemas import AIOrderResponse
from services.dish_service import get_all_dishes
from sqlmodel import Session

# Try to initialize the client. It will automatically use GEMINI_API_KEY from environment
try:
    client = genai.Client()
except Exception as e:
    client = None
    print(f"Failed to initialize Gemini Client: {e}")

MODEL_NAME = "gemini-3.1-flash-lite" # The requested Flash Lite model

async def parse_order_with_ai(session: Session, text: Optional[str] = None, audio: Optional[UploadFile] = None) -> AIOrderResponse:
    if not client:
        raise ValueError("Gemini API key is not configured or client failed to initialize.")

    if not text and not audio:
        raise ValueError("Must provide either text or audio to parse.")

    # Fetch available dishes to provide context to the AI
    dishes = get_all_dishes(session)
    menu_list = [{"id": d.id, "name": d.name, "price": d.price} for d in dishes if d.available]
    menu_text = "CURRENT MENU (JSON FORMAT):\n" + json.dumps(menu_list, indent=2)

    system_instruction = (
        "You are an intelligent order-taking assistant for a restaurant serving local and traditional food. "
        "You will be given either a spoken order (audio) or a written order (text). "
        "Your task is to identify exactly which dishes from the CURRENT MENU the customer wants, "
        "along with their requested quantities. "
        "Return a JSON object containing the exact 'transcription' of what the user said (or wrote), "
        "and an 'items' array containing the exact 'dish_id', 'name', and 'quantity'. "
        "If they ask for something not on the menu, ignore it or do your best to match it to the closest item. "
        f"\n{menu_text}"
    )

    contents = []

    if audio:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            content = await audio.read()
            if len(content) == 0:
                raise ValueError("The recorded audio file is empty. Please check your microphone permissions.")
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        # Upload the audio file to Gemini using the Files API
        uploaded_file = client.files.upload(
            file=temp_audio_path,
            config={'mime_type': audio.content_type, 'display_name': audio.filename}
        )
        
        # Wait for the file to be processed
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(1)
            uploaded_file = client.files.get(name=uploaded_file.name)
            
        if uploaded_file.state.name == "FAILED":
            error_details = getattr(uploaded_file, "error", "Unknown error")
            raise ValueError(f"Audio file processing failed by Gemini. Details: {error_details}")

        contents.append(uploaded_file)
        
        if text:
            contents.append(text)
        else:
            contents.append("Please transcribe and parse this audio order.")
    else:
        contents.append(text)

    # Generate content forcing the JSON schema
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AIOrderResponse,
            system_instruction=system_instruction
        )
    )

    # If we uploaded a file, it's good practice to delete it from Gemini's storage afterwards
    if audio:
        try:
            client.files.delete(name=uploaded_file.name)
            os.remove(temp_audio_path)
        except Exception:
            pass

    return AIOrderResponse.model_validate_json(response.text)
