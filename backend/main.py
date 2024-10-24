from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from urllib.parse import quote
import chromadb
import os
import google.generativeai as genai
from rag_utils import safety_settings, rag_generation_config, generate_model_response, create_database
from agent_utils import determine_action_from_query, decision_generation_config
from TTS import text_to_speech
import httpx
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
genai.configure(api_key=os.environ["GEMINI_KEY"])

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

proxy = "http://localhost:8000"

decision_model = genai.GenerativeModel('gemini-1.5-flash-002', safety_settings=safety_settings, generation_config=decision_generation_config)
rag_model = genai.GenerativeModel('gemini-1.5-flash-8b', safety_settings=safety_settings, generation_config=rag_generation_config)

client = chromadb.PersistentClient(path="./chromadb")

decision_chat = decision_model.start_chat()

try:
    collection = client.get_collection("pdfs")
except Exception as e:
    create_database("pdfs", "./chromadb", "./pdfs")
    collection = client.get_collection("pdfs")

class Query(BaseModel):
    query: str

@app.post("/retrieve") # endpoint for retriever
async def retrieve(query_data: Query = None):
    try: 
        query = query_data.query
        results = collection.query(query_texts=[query], n_results= 5)
        all_text = " ".join([line for result in results['documents'] for line in result])
        return JSONResponse(content={"response": all_text})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.post("/rag")
async def rag_endpoint(query_data: Query = None):
    try:
        query = query_data.query
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{proxy}/retrieve", json={"query": query})
        
        context_text = response.json()["response"]
        generated_content = generate_model_response(rag_model, query, context_text)
        return JSONResponse(content={"response": generated_content})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.post("/agent")
async def agent_endpoint(query_data: Query = None):
    try:
        query = query_data.query
        response = await determine_action_from_query(decision_chat, query) 
        return JSONResponse(content={"response": response})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.post("/tts")
async def tts_endpoint(query_data: Query = None):
    try:
        query = query_data.query
        resp = await text_to_speech(query)
        audio = resp["audios"][0]
        return JSONResponse(content={"response": audio})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)    
