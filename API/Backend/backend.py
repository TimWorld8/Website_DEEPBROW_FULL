import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import Response
import cv2
import numpy as np
import os
import io
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import detect_eyebrow
import httpx
from typing import Union

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def switch_model(file: UploadFile, style: str, eyebrow: str, model: int) -> Union[bytes, None]:
    # Read file content
    file_content = await file.read()
    
    # สร้าง form data สำหรับส่งไฟล์
    files = {
        'file': (file.filename, file_content, file.content_type)
    }
    data = {
        'style': style,
        'eyebrow': eyebrow,
        'model': model
    }
    
    # เลือก URL ตามโมเดล
    if model == 0:
        url = 'http://127.0.0.1:9000/model1/'
    elif model == 1:
        url = 'http://127.0.0.1:9002/model2/'
    elif model == 2:
        url = 'http://127.0.0.1:9004/model3/'
    else:
        raise HTTPException(status_code=400, detail="Invalid model selection")
    
    try:
        async with httpx.AsyncClient() as client:
            try:
                # Set proper headers for multipart form data
                headers = {
                    'Accept': 'image/*'
                }
                response = await client.post(
                    url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=30.0
                )
                
                # Check if response is an image
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    raise HTTPException(
                        status_code=500,
                        detail=f"Expected image response, got {content_type}"
                    )
                
                return response.content
                
            except httpx.ConnectError:
                raise HTTPException(
                    status_code=503,
                    detail=f"Model service is not running at {url}. Please ensure the model server is started."
                )
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=504,
                    detail=f"Request to model service timed out. The service at {url} is not responding."
                )
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Model service error: {str(e)}"
                )
    except Exception as e:
        # Seek file pointer back to start in case we need to retry
        await file.seek(0)
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while calling model API: {str(e)}"
        )

@app.post("/remove-eyebrow/")
async def remove_eyebrow(
    file: UploadFile = File(...),
    style: str = Form(...),
    eyebrow: str = Form(...),
    model: int = Form(...)
):
    # เพิ่ม logging เพื่อดูข้อมูลที่ได้รับ
    logging.info(f"Received request - File: {file.filename}, Style: {style}, Eyebrow: {eyebrow}, Model: {model}")
    
    # Validate model value
    if not isinstance(model, int) or model not in [0, 1, 2]:
        raise HTTPException(status_code=400, detail="Model must be 0, 1, or 2")
    
    result = await switch_model(file, style, eyebrow, model)
    if result:
        return Response(content=result, media_type="image/png")
    raise HTTPException(status_code=500, detail="Failed to process image")

# Simple GET Endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application. Use POST requests to interact with the image processing endpoints."}

# รันเซิร์ฟเวอร์
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)