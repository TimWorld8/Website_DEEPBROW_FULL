import cv2
import numpy as np

def remove_white_background(image_path, output_path):
    # อ่านรูปภาพ
    img = cv2.imread(image_path)
    
    # แปลงรูปภาพเป็น RGBA (เพิ่ม alpha channel)
    rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    
    # สร้าง mask สำหรับสีขาวในช่วงที่กว้างขึ้น
    lower_white = np.array([150, 150, 150])  # ค่าสีขาวล่าง (ใกล้เคียงสีขาวมากขึ้น)
    upper_white = np.array([255, 255, 255])  # ค่าสีขาวบน
    
    # หา pixels ที่เป็นสีขาวหรือใกล้เคียงสีขาว
    mask = cv2.inRange(img, lower_white, upper_white)
    
    # ทำให้ alpha channel เป็น 0 (โปร่งใส) สำหรับ pixels ที่เป็นสีขาว
    rgba[:, :, 3] = 255 - mask
    
    # บันทึกรูปภาพ
    cv2.imwrite(output_path, rgba)

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    input_image = "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/flat-rmbg.png"
    output_image = "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Frontend/deepbrow-frontend/src/image/eyebrow/flat-rmbg-remove-white.png"
    
    remove_white_background(input_image, output_image)