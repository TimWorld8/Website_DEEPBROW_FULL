import cv2
import numpy as np

# โหลดภาพ
image = cv2.imread('C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/remove_backgournd/steep_arch.png', cv2.IMREAD_UNCHANGED)

# ตรวจสอบว่าโหลดภาพสำเร็จหรือไม่
if image is None:
    print("Error: ไม่พบไฟล์ภาพ")
    exit()

# แปลงเป็น Grayscale เพื่อตรวจจับพื้นหลังสีขาว
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# สร้าง Mask โดยใช้ Thresholding (พื้นหลังสีขาว → 255, ส่วนอื่น → 0)
_, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

# อินเวิร์ส Mask (เปลี่ยน 0 → 255 และ 255 → 0)
mask_inv = cv2.bitwise_not(mask)

# แยกเฉพาะส่วนของภาพที่ไม่ใช่พื้นหลัง
result = cv2.bitwise_and(image, image, mask=mask_inv)

# Check the number of channels in the result image
num_channels = result.shape[2] if len(result.shape) == 3 else 1

# Split the channels accordingly
if num_channels == 3:
    b, g, r = cv2.split(result)
    alpha = mask_inv  # Use the mask as the alpha channel
elif num_channels == 4:
    b, g, r, alpha = cv2.split(result)
else:
    print("Unexpected number of channels in the result image.")
    exit()

output = cv2.merge([b, g, r, alpha])

# บันทึกภาพเป็น PNG โปร่งใส
cv2.imwrite("API/Frontend/deepbrow-frontend/src/image/eyebrow/steep_arch-rmbg.png", output)

# แสดงผลลัพธ์
cv2.imshow("Transparent Image", output)
cv2.waitKey(0)
cv2.destroyAllWindows()
