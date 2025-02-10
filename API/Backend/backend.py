import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
import cv2
import numpy as np
import os
import io
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import detect_eyebrow

# ตั้งค่า logging (ให้กำหนดครั้งเดียว)
logging.basicConfig(level=logging.INFO)

# ซ่อน Error [WinError 10054]
class IgnoreWinErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "WinError 10054" not in record.getMessage()

# Apply logging filter to asyncio & uvicorn
asyncio_logger = logging.getLogger("asyncio")
asyncio_logger.addFilter(IgnoreWinErrorFilter())

uvicorn_logger = logging.getLogger("uvicorn.error")
uvicorn_logger.addFilter(IgnoreWinErrorFilter())

# สร้าง FastAPI app
app = FastAPI()

# เพิ่ม CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ฟังก์ชันสำหรับลบคิ้ว
def remove_eyebrow(image_array):
    if not image_array:
        raise ValueError("Empty image array received.")
    
    # เรียกใช้ detect_eyebrow_mask เพื่อได้ภาพและมาสก์
    image, eyebrow_mask = detect_eyebrow.detect_eyebrow_mask(image_array)
    
    if image is None:
        raise ValueError("Failed to decode image. The image data might be corrupted or not in a valid format.")
    
    # แปลง mask เป็น 3 channels สำหรับ inpainting
    eyebrow_mask = cv2.cvtColor(eyebrow_mask, cv2.COLOR_GRAY2BGR)
    
    # ปรับแต่ง mask
    kernel = np.ones((2,2), np.uint8)
    eyebrow_mask = cv2.dilate(eyebrow_mask, kernel, iterations=1)

    # ทำ inpainting
    result1 = cv2.inpaint(image, eyebrow_mask[:,:,0], inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    result2 = cv2.inpaint(image, eyebrow_mask[:,:,0], inpaintRadius=7, flags=cv2.INPAINT_NS)
    result = cv2.addWeighted(result1, 0.8, result2, 0.2, 0)

    return result

# API สำหรับลบคิ้ว
@app.post("/remove-eyebrow/")
async def api_remove_eyebrow(file: UploadFile = File(...)):
    # ตรวจสอบขนาดไฟล์ (จำกัดที่ 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # อ่านไฟล์และตรวจสอบขนาด
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    if not contents:
        raise HTTPException(status_code=400, detail="No image data received.")

    try:
        processed_image = remove_eyebrow(contents)
        _, encoded_img = cv2.imencode(".jpg", processed_image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return Response(content=encoded_img.tobytes(), media_type="image/jpeg")
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Simple GET Endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application. Use POST requests to interact with the image processing endpoints."}

# รันเซิร์ฟเวอร์
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
