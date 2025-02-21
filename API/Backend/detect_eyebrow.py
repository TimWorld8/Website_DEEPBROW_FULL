import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import cv2
import numpy as np
from ultralytics import YOLO
import io
import logging

def detect_eyebrow_mask(image_bytes):
    try:
        # Validate input
        if image_bytes is None or len(image_bytes) == 0:
            raise ValueError("Empty image bytes received.")
        
        # Convert bytes to numpy array
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as decode_error:
            logging.error(f"Image decoding error: {decode_error}")
            raise ValueError(f"Failed to decode image bytes: {decode_error}")
        
        # Validate decoded image
        if image is None or image.size == 0:
            raise ValueError("Decoded image is empty or invalid.")
        
        # Log image details for debugging
        logging.info(f"Decoded image shape: {image.shape}")
        logging.info(f"Decoded image dtype: {image.dtype}")
        
        # Load YOLO model with error handling
        try:
            model = YOLO('C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Backend/best.pt')
        except Exception as model_load_error:
            logging.error(f"Model loading error: {model_load_error}")
            raise ValueError(f"Failed to load YOLO model: {model_load_error}")
        
        # Run model prediction with error handling
        try:
            results = model.predict(source=image, conf=0.6)
        except Exception as prediction_error:
            logging.error(f"Model prediction error: {prediction_error}")
            raise ValueError(f"Failed to run model prediction: {prediction_error}")
        
        h, w = image.shape[:2]  # Image dimensions
        
        # Create mask
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Process results
        eyebrow_found = False
        for result in results:
            if result.masks is None:
                continue  # Skip if no segmentation mask
            
            for box, mask_pred in zip(result.boxes, result.masks.xy):
                class_id = int(box.cls[0].item())
                class_name = model.names[class_id]
                
                if class_name == "eyebrow":
                    eyebrow_found = True
                    # Convert Polygon to NumPy Array
                    eyebrow_contour = np.array(mask_pred, dtype=np.int32)
                    
                    # Fill eyebrow mask
                    cv2.fillPoly(mask, [eyebrow_contour], 255)
        
        # Check if any eyebrows were found
        if not eyebrow_found:
            logging.warning("No eyebrows detected in the image.")
            # Create a default mask covering a typical eyebrow region
            h, w = image.shape[:2]
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.rectangle(mask, (w//4, h//4), (3*w//4, h//3), 255, -1)
        
        # Refine mask
        mask = cv2.GaussianBlur(mask, (3, 3), 0)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.dilate(mask, kernel, iterations=1)
        
        return image, mask
    
    except Exception as e:
        logging.error(f"Comprehensive error in detect_eyebrow_mask: {e}")
        raise 