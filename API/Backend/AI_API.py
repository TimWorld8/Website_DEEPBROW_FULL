import logging
import os
import asyncio
import io

import numpy as np
import cv2
from PIL import Image

import torch
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input
from diffusers import AutoPipelineForInpainting
import mediapipe as mp
from diffusers import StableDiffusionInpaintPipeline


from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

import detect_eyebrow


# โหลดโมเดล Inpainting
# pipe = StableDiffusionInpaintPipeline.from_pretrained(
#     "stabilityai/stable-diffusion-2-inpainting",
#     torch_dtype=torch.float16
# ).to("cuda")  # ใช้ GPU เพื่อให้เร็วขึ้น

pipe = AutoPipelineForInpainting.from_pretrained("diffusers/stable-diffusion-xl-1.0-inpainting-0.1", torch_dtype=torch.float16, variant="fp16").to("cuda")


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
def generate_eyebrow(image, mask_image, prompt):
    try:
        # Convert OpenCV images (BGR) to PIL Images (RGB)
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        mask_pil = Image.fromarray(cv2.cvtColor(mask_image, cv2.COLOR_BGR2RGB))

        # Check if prompt is provided and not empty
        if not prompt or prompt.strip() == "":
            prompt = "soft angle eyebrow and black color with natural and realistic eyebrows, high quality, photorealistic"
        else:
            # Add quality keywords to user prompt
            prompt = f"{prompt.strip()}, natural and realistic eyebrows, high quality, photorealistic"

        # Set up generator for reproducibility
        generator = torch.Generator(device="cuda").manual_seed(0)

        # Run the inpainting pipeline
        output = pipe(
            prompt=prompt,
            image=image_pil,
            mask_image=mask_pil,
            guidance_scale=8.0,
            num_inference_steps=20,
            strength=0.99,
            generator=generator,
        ).images[0]

        # Convert PIL Image output back to numpy array
        output_np = np.array(output)
        
        return output_np

    except Exception as e:
        logging.error(f"Error in generate_eyebrow: {str(e)}")
        # Return original image if generation fails
        return image

# ฟังก์ชันสำหรับลบคิ้ว
def remove_eyebrow(image_array):
    try:
        if image_array is None or len(image_array) == 0:
            raise ValueError("Empty image array received.")
        
        # Decode image with error handling
        try:
            nparr = np.frombuffer(image_array, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as decode_error:
            logging.error(f"Image decoding error: {decode_error}")
            raise ValueError(f"Failed to decode image: {decode_error}")
        
        if image is None or image.size == 0:
            raise ValueError("Decoded image is empty or invalid.")
        
        # Ensure image is in color
        if len(image.shape) < 3:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # Convert image to bytes for detect_eyebrow_mask
        try:
            _, image_bytes = cv2.imencode('.png', image)
            image_bytes = image_bytes.tobytes()
        except Exception as conversion_error:
            logging.error(f"Image conversion to bytes error: {conversion_error}")
            raise ValueError(f"Failed to convert image to bytes: {conversion_error}")
        
        # Detect eyebrow mask with error handling
        try:
            image, eyebrow_mask = detect_eyebrow.detect_eyebrow_mask(image_bytes)
        except Exception as eyebrow_error:
            logging.error(f"Eyebrow detection error: {eyebrow_error}")
            # Log the image details for debugging
            logging.error(f"Image shape: {image.shape if 'image' in locals() else 'N/A'}")
            logging.error(f"Image dtype: {image.dtype if 'image' in locals() else 'N/A'}")
            raise ValueError(f"Failed to detect eyebrow mask: {eyebrow_error}")
        
        if image is None or eyebrow_mask is None:
            raise ValueError("Failed to process eyebrow mask.")
        
        # Ensure mask is grayscale and convert to 3 channels
        if len(eyebrow_mask.shape) > 2:
            eyebrow_mask = cv2.cvtColor(eyebrow_mask, cv2.COLOR_BGR2GRAY)
        eyebrow_mask = cv2.cvtColor(eyebrow_mask, cv2.COLOR_GRAY2BGR)
        
        # Adjust mask
        kernel = np.ones((2,2), np.uint8)
        eyebrow_mask = cv2.dilate(eyebrow_mask, kernel, iterations=1)

        # Inpainting with multiple methods
        result1 = cv2.inpaint(image, eyebrow_mask[:,:,0], inpaintRadius=5, flags=cv2.INPAINT_TELEA)
        result2 = cv2.inpaint(image, eyebrow_mask[:,:,0], inpaintRadius=7, flags=cv2.INPAINT_NS)
        result = cv2.addWeighted(result1, 0.8, result2, 0.2, 0)

        return result, eyebrow_mask
    
    except Exception as e:
        logging.error(f"Comprehensive error in remove_eyebrow: {e}")
        raise

def detect_face_shape(model_instance, image_array):
    try:
        # Validate input
        if image_array is None or image_array.size == 0:
            raise ValueError("Empty image array received.")
        
        # Ensure image is in color and has 3 channels
        if len(image_array.shape) < 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2BGR)
        
        # Resize and preprocess image
        try:
            image_resized = cv2.resize(image_array, (299, 299), interpolation=cv2.INTER_AREA)
        except Exception as resize_error:
            logging.error(f"Image resize error: {resize_error}")
            raise ValueError(f"Failed to resize image: {resize_error}")
        
        # Debug logging
        logging.info(f"Image shape after resize: {image_resized.shape}")
        logging.info(f"Image dtype: {image_resized.dtype}")
        
        # Convert to float and preprocess
        try:
            img_array = image.img_to_array(image_resized)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)
        except Exception as preprocess_error:
            logging.error(f"Image preprocessing error: {preprocess_error}")
            raise ValueError(f"Failed to preprocess image: {preprocess_error}")
        
        # Predict face shape with error handling
        try:
            predictions = model_instance.predict(img_array)
            class_names = ["Heart", "Oblong", "Oval", "Round", "Square"]
            predicted_class = class_names[np.argmax(predictions)]
            
            # Log prediction confidence
            confidence = np.max(predictions)
            logging.info(f"Predicted Face Shape: {predicted_class} with confidence: {confidence}")
            
            return predicted_class
        except Exception as predict_error:
            logging.error(f"Face shape prediction error: {predict_error}")
            raise ValueError(f"Failed to predict face shape: {predict_error}")
    
    except Exception as e:
        logging.error(f"Comprehensive error in detect_face_shape: {e}")
        raise

def add_eyebrow(image_array, face_shape, eyebrow):
    try:
        # Validate input
        if image_array is None or image_array.size == 0:
            raise ValueError("Empty image array received.")
        
        # Ensure image is in color
        if len(image_array.shape) < 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2BGR)
        
        # Convert the input image array to RGB
        face_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

        # Load Mediapipe Face Mesh with error handling
        try:
            mp_face_mesh = mp.solutions.face_mesh
            with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.01) as face_mesh:
                results = face_mesh.process(face_rgb)
        except Exception as mesh_error:
            logging.error(f"Face mesh detection error: {mesh_error}")
            raise ValueError(f"Failed to detect face landmarks: {mesh_error}")

        # Check if face landmarks are detected
        if not results.multi_face_landmarks:
            logging.warning("No face landmarks detected.")
            return image_array

        # Eyebrow path mapping with validation
        eyebrow_paths = {
            # Auto Style paths
            "Heart": "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/rounded-rmbg.png",
            "Round": "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/hardtangle-rmbg.png",
            "Oblong": "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/straight-rmbg.png",
            "Square": "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/softangle-rmbg.png",
            "Oval": "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/softangle-rmbg.png",
            
            # Manual Style paths
            "Flat Brow": "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/remove_white/flat-rmbg-remove-white.png",
            "Hard Angle": "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/remove_white/hardtangle-rmbg-remove-white.png",
            "Rounded Arch": "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/remove_white/rounded-rmbg-remove-white.png",
            "Soft Angle": "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/remove_white/softangle-rmbg-remove-white.png",
            "Steep Arch": "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/remove_white/steep_arch-rmbg-remove-white.png",
            "Straight Brow": "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/remove_white/straight-rmbg-remove-white.png"
        }

        # Determine eyebrow path
        if eyebrow == 'Auto Style':
            eyebrow_path = eyebrow_paths.get(face_shape)
        else:
            eyebrow_path = eyebrow_paths.get(eyebrow)

        # Validate eyebrow path
        if not eyebrow_path or not os.path.exists(eyebrow_path):
            logging.error(f"Invalid eyebrow path for {eyebrow} or {face_shape}")
            return image_array

        for face_landmarks in results.multi_face_landmarks:
            ih, iw, _ = image_array.shape

            # Determine eyebrow positions
            left_brow_x = int(face_landmarks.landmark[107].x * iw)
            left_brow_y = int(face_landmarks.landmark[107].y * ih)
            right_brow_x = int(face_landmarks.landmark[336].x * iw)
            right_brow_y = int(face_landmarks.landmark[336].y * ih)

            # Load eyebrow image
            try:
                eyebrow_img = cv2.imread(eyebrow_path, cv2.IMREAD_UNCHANGED)
                if eyebrow_img is None:
                    raise ValueError(f"Failed to load eyebrow image from {eyebrow_path}")
            except Exception as img_load_error:
                logging.error(f"Eyebrow image load error: {img_load_error}")
                return image_array

            # Existing eyebrow addition logic remains the same...
            x = 1.49  # Default scaling factor
            face_width = abs(right_brow_x - left_brow_x)
            dynamic_scale = (face_width * x) / eyebrow_img.shape[1]
            eyebrow_width = int(eyebrow_img.shape[1] * dynamic_scale)
            eyebrow_height = int(eyebrow_img.shape[0] * dynamic_scale)

            # สร้าง eyebrow สำหรับซ้ายโดยการ mirror จาก eyebrow image
            left_eyebrow = cv2.flip(eyebrow_img, 1)

            # Resize eyebrows ด้วย dynamic_scale
            right_eyebrow_resized = cv2.resize(left_eyebrow, (eyebrow_width, eyebrow_height), interpolation=cv2.INTER_AREA)
            left_eyebrow_resized = cv2.resize(eyebrow_img, (eyebrow_width, eyebrow_height), interpolation=cv2.INTER_AREA)

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

            # Blend eyebrows onto the face with proper alpha blending
            for c in range(3):  # Blend only BGR channels
                # Extract alpha channel and normalize
                alpha = right_eyebrow_resized[:, :, 3] / 255.0
                
                # Blend channels with alpha
                image_array[right_y_min:right_y_max, right_x_min:right_x_max, c] = (
                    image_array[right_y_min:right_y_max, right_x_min:right_x_max, c] * (1 - alpha) + 
                    right_eyebrow_resized[:, :, c] * alpha
                ).astype(np.uint8)

                # Same for left eyebrow
                alpha = left_eyebrow_resized[:, :, 3] / 255.0
                image_array[left_y_min:left_y_max, left_x_min:left_x_max, c] = (
                    image_array[left_y_min:left_y_max, left_x_min:left_x_max, c] * (1 - alpha) + 
                    left_eyebrow_resized[:, :, c] * alpha
                ).astype(np.uint8)

        return image_array
    
    except Exception as e:
        logging.error(f"Comprehensive error in add_eyebrow: {e}")
        return image_array  # Return original image if any error occurs


# API สำหรับลบคิ้ว
@app.post("/model1/")
async def api_remove_eyebrow(file: UploadFile = File(...), eyebrow: str = Form(None), style: str = Form(None), eyebrow_prompt: str = Form(None)):
    # Validate input parameters
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Set default values if not provided
    eyebrow = eyebrow or 'Auto Style'
    style = style or 'Soft Elegance'

    # Print received parameters for logging
    logging.info(f"Received parameters - Eyebrow: {eyebrow}, Style: {style}")

    # Validate file size
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    try:
        # Read file contents
        contents = await file.read()
        
        # Check file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        
        if not contents:
            raise HTTPException(status_code=400, detail="No image data received")

        # Process image
        processed_image, eyebrow_mask = remove_eyebrow(contents)
        
        # Determine eyebrow addition method
        if eyebrow != 'Generated':
            try:
                face_shape = detect_face_shape(model, processed_image)
                final_image = add_eyebrow(processed_image, face_shape, eyebrow)
                processed_image = final_image


                # pil_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
                # pil_mask = Image.fromarray(cv2.cvtColor(eyebrow_mask, cv2.COLOR_BGR2RGB))

                # # ใช้ Stable Diffusion เติมคิ้ว
                # generated_image = generate_eyebrow(pil_image, pil_mask, eyebrow_prompt)
                #                 # แปลง PIL Image -> NumPy Array (RGB)
                # generated_np = np.array(generated_image)

                # # ตรวจสอบว่า generated_np อยู่ในช่วง 0-255 และเป็น dtype uint8
                # if generated_np.dtype != np.uint8:
                #     generated_np = (generated_np * 255).astype(np.uint8)  # ป้องกันปัญหาการ Normalize เป็น 0-1

                # # บังคับให้ขนาดของภาพกลับไปเป็นขนาดเดิม
                # final_image = cv2.resize(generated_np, (processed_image.shape[1], processed_image.shape[0]), interpolation=cv2.INTER_AREA)

                # แปลงจาก RGB -> BGR กลับไปใช้กับ OpenCV
                # final_image = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR)
            except Exception as face_process_error:
                logging.error(f"Face processing error: {face_process_error}")
                final_image = processed_image  # Fallback to processed image
        else:
            try:
                # Convert processed_image to PIL Image for Stable Diffusion
                # แปลงภาพจาก OpenCV (BGR) -> PIL (RGB)
                # pil_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
                # pil_mask = Image.fromarray(cv2.cvtColor(eyebrow_mask, cv2.COLOR_BGR2RGB))

                # ใช้ Stable Diffusion เติมคิ้ว
                generated_image = generate_eyebrow(processed_image, eyebrow_mask, eyebrow_prompt)

                # # แปลง PIL Image -> NumPy Array (RGB)
                # generated_np = np.array(generated_image)
                generated_np = generated_image
                # ตรวจสอบว่า generated_np อยู่ในช่วง 0-255 และเป็น dtype uint8
                if generated_np.dtype != np.uint8:
                    generated_np = (generated_np * 255).astype(np.uint8)  # ป้องกันปัญหาการ Normalize เป็น 0-1

                # บังคับให้ขนาดของภาพกลับไปเป็นขนาดเดิม
                final_image = cv2.resize(generated_np, (processed_image.shape[1], processed_image.shape[0]), interpolation=cv2.INTER_AREA)

                # แปลงจาก RGB -> BGR กลับไปใช้กับ OpenCV
                final_image = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR)

            except Exception as gen_error:
                logging.error(f"Eyebrow generation error: {gen_error}")
                final_image = processed_image  # Fallback to processed image

        # Encode and return image
        _, encoded_img = cv2.imencode(".jpg", final_image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return Response(content=encoded_img.tobytes(), media_type="image/jpeg")
    
    except Exception as e:
        logging.error(f"Comprehensive API error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Simple GET Endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application. Use POST requests to interact with the image processing endpoints."}

# รันเซิร์ฟเวอร์
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
