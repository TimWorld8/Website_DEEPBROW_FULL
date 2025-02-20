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

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input

import mediapipe as mp

model = load_model("C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/model/shape_face.h5")
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

def detect_face_shape(model_instance, image_array):
    image_array = cv2.resize(image_array, (299, 299))
    if image_array is None or image_array.size == 0:
        raise ValueError("Empty image array received.")
    print(f"Debug - Image shape: {image_array.shape}")
    print(f"Debug - Image dtype: {image_array.dtype}")

    
    img_array = image.img_to_array(image_array)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # ทำนายผล
    predictions = model_instance.predict(img_array)
    class_names = ["Heart", "Oblong", "Oval", "Round", "Square"] #หัวใจ สี่เหลี่ยม ใบหน้ารูปไข่ หน้ากลม ใบหน้าสี่เหลี่ยม
    predicted_class = class_names[np.argmax(predictions)]
    print(f"Predicted Face Shape: {predicted_class}")
    return predicted_class

def add_eyebrow(image_array, face_shape):
    # Convert the input image array to RGB
    face_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

    # Load Mediapipe Face Mesh
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.01) as face_mesh:
        results = face_mesh.process(face_rgb)

    # Check if face landmarks are detected
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            ih, iw, _ = image_array.shape

            # Determine eyebrow positions (ปรับตำแหน่งตามที่ต้องการ)
            left_brow_x = int(face_landmarks.landmark[107].x * iw)
            left_brow_y = int(face_landmarks.landmark[107].y * ih)
            right_brow_x = int(face_landmarks.landmark[336].x * iw)
            right_brow_y = int(face_landmarks.landmark[336].y * ih)

            # เลือก eyebrow image ตาม face shape (ในตัวอย่างใช้ภาพเดียวกัน)
            if face_shape == "Heart":
                eyebrow_path = "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/rounded-rmbg.png"
                x = 1.45
            elif face_shape == "Round":
                eyebrow_path = "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/hardtangle-rmbg.png"
                x = 1.45
            elif face_shape == "Oblong":
                eyebrow_path = "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/Oblong.png"
                x = 1.45
            elif face_shape == "Square":
                eyebrow_path = "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/Square.png"
                x = 1.45
            
            # Load the eyebrow image with transparency
            eyebrow = cv2.imread(eyebrow_path, cv2.IMREAD_UNCHANGED)

            # คำนวณระยะห่างระหว่าง landmark ทั้งสองเพื่อใช้เป็นตัวอ้างอิง
            face_width = abs(right_brow_x - left_brow_x)
            # กำหนด multiplier (0.4 ในที่นี้) เพื่อปรับขนาด eyebrow ให้เหมาะสมกับใบหน้า
            dynamic_scale = (face_width * x) / eyebrow.shape[1]
            eyebrow_width = int(eyebrow.shape[1] * dynamic_scale)
            eyebrow_height = int(eyebrow.shape[0] * dynamic_scale)

            # สร้าง eyebrow สำหรับซ้ายโดยการ mirror จาก eyebrow image
            left_eyebrow = cv2.flip(eyebrow, 1)

            # Resize eyebrows ด้วย dynamic_scale
            right_eyebrow_resized = cv2.resize(left_eyebrow, (eyebrow_width, eyebrow_height), interpolation=cv2.INTER_AREA)
            left_eyebrow_resized = cv2.resize(eyebrow, (eyebrow_width, eyebrow_height), interpolation=cv2.INTER_AREA)

            # Apply Gaussian Blur to alpha channel
            right_eyebrow_resized[:, :, 3] = cv2.GaussianBlur(right_eyebrow_resized[:, :, 3], (3, 3), 2)
            left_eyebrow_resized[:, :, 3] = cv2.GaussianBlur(left_eyebrow_resized[:, :, 3], (3, 3), 2)

            # Calculate positions for right eyebrow
            right_x_min = right_brow_x
            right_x_max = min(right_brow_x + eyebrow_width, iw)
            right_y_min = max(right_brow_y - eyebrow_height // 2, 0)
            right_y_max = min(right_y_min + eyebrow_height, ih)

            # Calculate positions for left eyebrow
            left_x_min = left_brow_x - eyebrow_width
            left_x_max = left_brow_x
            left_y_min = max(left_brow_y - eyebrow_height // 2, 0)
            left_y_max = min(left_y_min + eyebrow_height, ih)

            # Blend eyebrows onto the face
            for c in range(3):  # Blend only BGR channels
                image_array[right_y_min:right_y_max, right_x_min:right_x_max, c] = np.where(
                    right_eyebrow_resized[:, :, 3] > 20,
                    cv2.addWeighted(image_array[right_y_min:right_y_max, right_x_min:right_x_max, c], 0.5, right_eyebrow_resized[:, :, c], 0.5, 0),
                    image_array[right_y_min:right_y_max, right_x_min:right_x_max, c]
                )
                image_array[left_y_min:left_y_max, left_x_min:left_x_max, c] = np.where(
                    left_eyebrow_resized[:, :, 3] > 20,
                    cv2.addWeighted(image_array[left_y_min:left_y_max, left_x_min:left_x_max, c], 0.5, left_eyebrow_resized[:, :, c], 0.5, 0),
                    image_array[left_y_min:left_y_max, left_x_min:left_x_max, c]
                )

    return image_array


# API สำหรับลบคิ้ว
@app.post("/model1/")
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
        face_shape = detect_face_shape(model, processed_image)
        final_image = add_eyebrow(processed_image, face_shape)
        _, encoded_img = cv2.imencode(".jpg", final_image, [cv2.IMWRITE_JPEG_QUALITY, 90])
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
    uvicorn.run(app, host="0.0.0.0", port=9000)
