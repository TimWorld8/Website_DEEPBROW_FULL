import cv2
import numpy as np
import os

def test_remove_eyebrow():
    # Use the file's directory to build absolute paths:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build paths relative to this script's folder.
    input_image_path = os.path.join(base_dir, '..', 'data_test', 'data_test\face.jpg')
    expected_output_path = os.path.join(base_dir, 'expected_output.png')
    
    # Call the remove_eyebrow function
    result_image = remove_eyebrow(input_image_path)
    
    # Instead of comparing, save the output
    cv2.imwrite(expected_output_path, result_image)
    print(f"Output image saved to: {expected_output_path}")
    

    
    print("Test case 1 completed: Eyebrow removal result saved.")

def remove_eyebrow(image_path):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Input image not found at: {image_path}")
    
    # Build the path for the eyebrow mask
    mask_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data_test', 'eyebrow_mask.png')
    eyebrow_mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if eyebrow_mask is None:
        raise FileNotFoundError(f"Eyebrow mask image not found at: {mask_path}")
    
    # Resize and smooth the eyebrow mask edges
    eyebrow_mask = cv2.resize(eyebrow_mask, (image.shape[1], image.shape[0]))
    eyebrow_mask = cv2.GaussianBlur(eyebrow_mask, (5, 5), 0)  # ทำให้ขอบ mask นุ่มขึ้น
    _, eyebrow_mask = cv2.threshold(eyebrow_mask, 127, 255, cv2.THRESH_BINARY)
    
    # ขยาย mask เล็กน้อยเพื่อครอบคลุมบริเวณคิ้วอย่างเหมาะสม
    kernel = np.ones((2,2), np.uint8)
    eyebrow_mask = cv2.dilate(eyebrow_mask, kernel, iterations=1)
    
    # ทำ inpainting ด้วย 2 วิธีเพื่อให้ได้ผลลัพธ์ที่หลอมรวมกัน
    result1 = cv2.inpaint(image, eyebrow_mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    result2 = cv2.inpaint(image, eyebrow_mask, inpaintRadius=7, flags=cv2.INPAINT_NS)
    result = cv2.addWeighted(result1, 0.8, result2, 0.2, 0)
    
    # สร้าง blending mask ที่นุ่มขึ้นโดยใช้ Gaussian Blur ที่ใหญ่ขึ้น
    mask_blur = cv2.GaussianBlur(eyebrow_mask, (21, 21), 0)
    mask_blur = mask_blur.astype(float) / 255.0
    
    # Blend: เพิ่มจำนวนรอบและใช้ kernel ขนาดใหญ่ขึ้นสำหรับ local blur
    for i in range(3):  # เพิ่มรอบจาก 2 เป็น 3 ครั้ง
        local_blur = cv2.GaussianBlur(result, (5, 5), 0)  # เปลี่ยน kernel จาก (3,3) เป็น (5,5)
        alpha = mask_blur[:, :, np.newaxis]
        result = result * (1 - alpha) + local_blur * alpha
    
    # ขั้นตอนเบลอขั้นสุดท้ายเพื่อให้ผลลัพธ์ดูเนียนมากขึ้น
    final_blend = cv2.GaussianBlur(result, (3, 3), 0)
    result = cv2.addWeighted(result, 0.85, final_blend, 0.15, 0)
    
    return result.astype(np.uint8)

def blend_skin_tone(image_path):
    # อ่านรูปภาพ
    img = cv2.imread(image_path)
    
    # แปลงเป็นโมเดลสี YCrCb (เหมาะสำหรับการตรวจจับสีผิว)
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    
    # กำหนดช่วงสีผิว
    lower = np.array([0, 133, 77], dtype=np.uint8)
    upper = np.array([255, 173, 127], dtype=np.uint8)
    
    # สร้างมาสก์สำหรับบริเวณที่เป็นสีผิว
    skin_mask = cv2.inRange(ycrcb, lower, upper)
    
    # ทำการ Blur เฉพาะบริเวณผิว
    blurred = cv2.GaussianBlur(img, (15, 15), 0)
    
    # รวมภาพต้นฉบับกับส่วนที่ Blur โดยใช้มาสก์
    result = img.copy()
    result[skin_mask > 0] = blurred[skin_mask > 0]
    
    return result

def remove_dark_eyebrows(image_path):
    # อ่านรูปภาพ
    img = cv2.imread(image_path)
    
    # แปลงเป็นภาพสีเทา
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # ใช้ threshold เพื่อแยกพื้นที่สีดำ
    _, dark_mask = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY_INV)
    
    # ทำให้มาสก์ละเอียดขึ้นด้วย morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel)
    
    # สร้างมาสก์สำหรับบริเวณที่ต้องการแก้ไข
    inpaint_mask = dark_mask.astype(np.uint8)
    
    # ใช้ inpainting เพื่อแทนที่บริเวณสีดำ
    result = cv2.inpaint(img, inpaint_mask, 3, cv2.INPAINT_TELEA)
    
    # ทำให้ภาพดูนุ่มนวลขึ้น
    result = cv2.GaussianBlur(result, (3,3), 0)
    
    return result

if __name__ == '__main__':
    test_remove_eyebrow()