from diffusers import StableDiffusionInpaintPipeline
import torch

# โหลดโมเดล Inpainting
pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-inpainting",
    torch_dtype=torch.float16
).to("cuda")  # ใช้ GPU เพื่อให้เร็วขึ้น


# import cv2
# import mediapipe as mp
# import numpy as np

# # โหลดรูปภาพที่ไม่มีคิ้ว
# image = cv2.imread("C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Backend/add_eyebrow/expected_output.png")

# # ใช้ Mediapipe Face Mesh
# mp_face_mesh = mp.solutions.face_mesh
# with mp_face_mesh.FaceMesh(min_detection_confidence=0.5) as face_mesh:
#     image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     results = face_mesh.process(image_rgb)

#     # ตรวจสอบว่าพบใบหน้าหรือไม่
#     if results.multi_face_landmarks:
#         for face_landmarks in results.multi_face_landmarks:
#             ih, iw, _ = image.shape

#             # หาตำแหน่งคิ้วซ้ายและขวา
#             left_eyebrow = [(face_landmarks.landmark[i].x * iw, face_landmarks.landmark[i].y * ih)
#                             for i in [70, 63, 105, 66, 107, 46, 53, 52, 65, 55]]  # รวมจุดบนและล่างของคิ้วซ้าย
#             right_eyebrow = [(face_landmarks.landmark[i].x * iw, face_landmarks.landmark[i].y * ih)
#                             for i in [336, 296, 334, 293, 300, 285, 295, 282, 283, 276]]  # รวมจุดบนและล่างของคิ้วขวา

#             # สร้าง Mask สีขาวตรงบริเวณที่ไม่มีคิ้ว
#             mask = np.zeros_like(image[:, :, 0])  # สร้าง mask ขนาดเท่ากับภาพ (ช่องเดียว grayscale)
#             cv2.fillPoly(mask, [np.array(left_eyebrow, np.int32)], 255)  # วาด Mask คิ้วซ้าย
#             cv2.fillPoly(mask, [np.array(right_eyebrow, np.int32)], 255)  # วาด Mask คิ้วขวา

#             # ขยาย mask เล็กน้อยเพื่อครอบคลุมบริเวณคิ้วอย่างเหมาะสม
#             kernel = np.ones((5, 5), np.uint8)
#             mask = cv2.dilate(mask, kernel, iterations=1)

#             # บันทึกภาพ Mask
#             cv2.imwrite("eyebrow_mask.png", mask)

# # แสดง Mask ที่สร้าง
# cv2.imshow("Eyebrow Mask", mask)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# from PIL import Image

# # โหลดภาพใบหน้าและ Mask ที่สร้าง
# init_image = Image.open("C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Backend/add_eyebrow/expected_output.png")
# mask_image = Image.open("C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/eyebrow_mask.png")

# # ใช้ Stable Diffusion Inpainting เติมคิ้ว
# prompt = "A face with natural and realistic eyebrows, high quality, photorealistic"
# output = pipe(prompt=prompt, image=init_image, mask_image=mask_image).images[0]

# # แสดงผลลัพธ์
# output.show()
# output.save("face_with_eyebrows.jpg")  # บันทึกภาพที่มีคิ้ว



