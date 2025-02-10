import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import cv2
import numpy as np
from ultralytics import YOLO
# โหลดโมเดล YOLO
model = YOLO('model/best.pt')

# รันโมเดลและรับผลลัพธ์
results = model.predict(
    source='data_test\depositphotos_141416106-stock-photo-beautiful-woman-touching-face.jpg',
    conf=0.6
)

# โหลดภาพต้นฉบับ
image = cv2.imread("data_test\depositphotos_141416106-stock-photo-beautiful-woman-touching-face.jpg")

# สร้าง mask
mask = np.zeros(image.shape[:2], dtype=np.uint8)

# สร้างลิสต์สำหรับตำแหน่งคิ้ว
eyebrow_coords = []

# ขนาดขยาย bounding box (ลองปรับได้)
expand_px = 5

for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        class_id = int(box.cls[0].item())
        class_name = model.names[class_id]

        if class_name == "eyebrow":
            # ขยาย bounding box รอบคิ้วให้กว้างขึ้นเล็กน้อย
            x1 = max(0, x1 - expand_px)
            y1 = max(0, y1 - expand_px)
            x2 = min(image.shape[1], x2 + expand_px)
            y2 = min(image.shape[0], y2 + expand_px)

            eyebrow_coords.append((x1, y1, x2, y2))
            mask[y1:y2, x1:x2] = 255

# ลองทำ dilation บน mask เพื่อขยายพื้นที่สีขาวสักหน่อย
kernel = np.ones((5, 5), np.uint8)  # ขนาด kernel สามารถปรับได้
mask = cv2.dilate(mask, kernel, iterations=1)

# ลอง Inpaint แบบ TELEA
inpaint_radius = 5  # ปรับรัศมีให้เหมาะสม
output = cv2.inpaint(image, mask, inpaint_radius, cv2.INPAINT_TELEA)

cv2.imwrite("add_eyebrow/eyebrow_mask_expanded.png", mask)
cv2.imwrite("add_eyebrow/eyebrow_removed_expanded.png", output)

print("ตำแหน่งคิ้วที่ตรวจพบ (ขยายแล้ว):", eyebrow_coords)
print("บันทึก mask และภาพที่ลบคิ้วแล้วเรียบร้อย!")
