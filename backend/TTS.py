import httpx
from fastapi import HTTPException
import os

SARVAM_KEY = os.environ["SARVAM_KEY"]

async def text_to_speech(text: str, target_language_code: str = "en-IN", speaker: str = "meera", enable_preprocessing : str = True, model : str = "bulbul:v1") -> dict:
    url = "https://api.sarvam.ai/text-to-speech"
    headers = {
        "api-subscription-key": SARVAM_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": [text],
        "target_language_code": target_language_code,  # Or other language
        "speaker": speaker,
        "enable_preprocessing": enable_preprocessing,
        "model": model
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            print("successfully recieved audio")
            return response.json()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    