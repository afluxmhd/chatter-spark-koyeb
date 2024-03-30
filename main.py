from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict
import requests

# Define the FastAPI app
app = FastAPI()

# Dependency to extract the API key from the request headers
def get_api_key(request: Request):
    api_key = request.headers.get('Authorization')
    if not api_key:
        raise HTTPException(status_code=400, detail="API key missing from headers")
    if not api_key.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="API key format is 'Bearer <API_KEY>'")
    return api_key.split(" ")[1]

# Model query function that accepts API key as an argument
def query(payload, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    API_URL = "https://api-inference.huggingface.co/models/vennify/t5-base-grammar-correction"
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error from the Hugging Face API")
    return response.json()

class CorrectionRequest(BaseModel):
    fix: str


@app.get("/")
async def check_server():
    response = {"Status":"Server is runningg.."}
    return response


# Endpoint to correct text, using the API key from the headers
@app.post("/text-correction", response_model=Dict[str, str])
async def correct_text(request: CorrectionRequest, api_key: str = Depends(get_api_key)):
    output = query({"inputs": request.fix}, api_key)

    if not output or not isinstance(output, list) or 'generated_text' not in output[0]:
        raise HTTPException(status_code=500, detail="Unexpected response structure from the Hugging Face API")

    corrected_text = output[0]['generated_text']

    return {"text": corrected_text}

    