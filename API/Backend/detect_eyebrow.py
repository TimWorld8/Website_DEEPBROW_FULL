import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import cv2
import numpy as np
from ultralytics import YOLO
import io

def detect_eyebrow_mask(image_bytes):
    # แปลง bytes เป็น numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # โหลดโมเดล YOLOv8 ที่ฝึกมาแล้ว
    model = YOLO('best.pt')

    # รันโมเดลและรับผลลัพธ์
    results = model.predict(source=image, conf=0.6)

    h, w = image.shape[:2]  # ขนาดของภาพ

    # สร้าง mask ขนาดเท่ากับภาพต้นฉบับ
    mask = np.zeros((h, w), dtype=np.uint8)

    for result in results:
        if result.masks is None:
            continue  # ข้ามถ้าไม่มี Segmentation Mask

        for box, mask_pred in zip(result.boxes, result.masks.xy):
            class_id = int(box.cls[0].item())  # ID ของคลาส
            class_name = model.names[class_id]  # ชื่อคลาส

            if class_name == "eyebrow":  # ตรวจสอบว่าคือลักษณะ "คิ้ว"
                # แปลง Polygon (Points) จาก YOLO เป็น NumPy Array
                eyebrow_contour = np.array(mask_pred, dtype=np.int32)

                # วาด mask ทรงคิ้วลงใน mask หลัก
                cv2.fillPoly(mask, [eyebrow_contour], 255)

    # ทำให้ Mask ละเอียดขึ้น
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=1)

    return image, mask 