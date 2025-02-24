import cv2
import numpy as np

def remove_white_background(image_path, output_path):
    # อ่านรูปภาพ
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    # แปลงรูปภาพเป็น RGBA
    if img.shape[2] == 3:  # ถ้าไม่มี alpha channel ให้เพิ่ม
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # กำหนดช่วงสีขาวที่ต้องการลบ
    lower_white = np.array([150, 150, 150, 0], dtype=np.uint8)
    upper_white = np.array([255, 255, 255, 255], dtype=np.uint8)

    # สร้าง Mask
    mask = cv2.inRange(img[:, :, :3], lower_white[:3], upper_white[:3])

    # ใช้ Mask เพื่อลบพื้นหลังสีขาว
    img[:, :, 3] = cv2.bitwise_and(img[:, :, 3], 255 - mask)

    # บันทึกภาพที่ได้
    cv2.imwrite(output_path, img)

# ตัวอย่างการใช้งาน
image_name = "straight-rmbg"
input_image = f"C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/{image_name}.png"
output_image = f"C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/remove_white/{image_name}-remove-white.png"

remove_white_background(input_image, output_image)

            # # Apply Gaussian Blur to alpha channel with larger kernel for smoother edges
            # right_eyebrow_resized[:, :, 3] = cv2.GaussianBlur(right_eyebrow_resized[:, :, 3], (5, 5), 2)
            # left_eyebrow_resized[:, :, 3] = cv2.GaussianBlur(left_eyebrow_resized[:, :, 3], (5, 5), 2)

            # # Create feathered edges
            # kernel = np.ones((3,3), np.uint8)
            # right_eyebrow_resized[:, :, 3] = cv2.erode(right_eyebrow_resized[:, :, 3], kernel, iterations=1)
            # left_eyebrow_resized[:, :, 3] = cv2.erode(left_eyebrow_resized[:, :, 3], kernel, iterations=1)