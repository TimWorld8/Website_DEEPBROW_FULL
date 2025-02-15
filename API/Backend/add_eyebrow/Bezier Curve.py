import cv2
import numpy as np
import matplotlib.pyplot as plt

# โหลดภาพที่มีคิ้ว
face_path = "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Backend/add_eyebrow.png"
face = cv2.imread(face_path, cv2.IMREAD_UNCHANGED)

# ตรวจสอบว่าภาพโหลดสำเร็จหรือไม่
if face is None:
    print("❌ Error: ไม่สามารถโหลดภาพ")
    exit()

# แปลงเป็น grayscale เพื่อหา edge ของคิ้ว
gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, threshold1=30, threshold2=100)

# สร้าง Perlin Noise เพื่อใช้เป็นพื้นฐานของขนคิ้ว
rows, cols = face.shape[:2]
noise = np.random.normal(loc=0, scale=25, size=(rows, cols)).astype(np.uint8)

# รวม Edge ของคิ้วกับ Noise เพื่อสร้างเส้นขนคิ้ว
eyebrow_hair = cv2.bitwise_and(noise, noise, mask=edges)

# ทำให้เส้นขนคิ้วดูสมจริงขึ้นโดยใช้ Blur
eyebrow_hair = cv2.GaussianBlur(eyebrow_hair, (5, 5), 2)

# เพิ่มเส้นขนคิ้วลงในภาพหลัก
for c in range(3):  # ใช้กับช่อง BGR
    face[:, :, c] = np.where(eyebrow_hair > 50,  # ถ้าค่ามีความเข้มพอ
                              cv2.addWeighted(face[:, :, c], 0.7, eyebrow_hair, 0.3, 0),  # ผสมเส้นคิ้วเข้ากับภาพ
                              face[:, :, c])

# บันทึกภาพที่มีขนคิ้วเพิ่มขึ้น
output_path = "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Backend/add_eyebrow_line.png"
cv2.imwrite(output_path, face)

# แสดงผลลัพธ์
plt.figure(figsize=(8,6))
plt.imshow(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
plt.axis("off")
plt.title("Face with Generated Eyebrow Hair")
plt.show()
