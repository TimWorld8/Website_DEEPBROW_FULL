import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt

# โหลดภาพใบหน้า
face_path = "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Backend/add_eyebrow/expected_output.png"
face = cv2.imread(face_path, cv2.IMREAD_UNCHANGED)

# โหลดภาพคิ้ว PNG (ต้องมี Transparency)
eyebrow_path = "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Backend/add_eyebrow/style/eyesbrow-1-rmbg.png"
eyebrow = cv2.imread(eyebrow_path, cv2.IMREAD_UNCHANGED)

# ตรวจสอบว่าไฟล์โหลดสำเร็จหรือไม่
if face is None or eyebrow is None:
    print("❌ Error: ไม่สามารถโหลดภาพ")
    exit()

# แปลงภาพเป็น RGB
face_rgb = cv2.cvtColor(face, cv2.COLOR_BGRA2RGB)

# โหลด Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5) as face_mesh:
    results = face_mesh.process(face_rgb)

# ตรวจสอบว่าพบใบหน้าหรือไม่
if results.multi_face_landmarks:
    for face_landmarks in results.multi_face_landmarks:
        ih, iw, _ = face.shape

        # หาตำแหน่งของจุดเริ่มต้นของคิ้ว (จุด 285)
        start_x = int(face_landmarks.landmark[336].x * iw)  # ตำแหน่ง x ของคิ้ว
        start_y = int(face_landmarks.landmark[336].y * ih)  # ตำแหน่ง y ของคิ้ว

        # **ลดขนาดคิ้วอย่างมีคุณภาพ (ใช้ INTER_AREA)**
        scale_factor = 0.25
        eyebrow_width = int(eyebrow.shape[1] * scale_factor)
        eyebrow_height = int(eyebrow.shape[0] * scale_factor)

        # คำนวณตำแหน่งวางคิ้ว
        left_x_min = start_x
        left_x_max = min(start_x + eyebrow_width, iw)
        left_y_min = max(start_y - eyebrow_height // 2, 0)
        left_y_max = min(left_y_min + eyebrow_height, ih)

        # **ลดขนาดคิ้วแบบคุณภาพสูง**
        eyebrow_resized = cv2.resize(eyebrow, (left_x_max - left_x_min, left_y_max - left_y_min), interpolation=cv2.INTER_AREA)

        # **ปรับ Alpha ให้คิ้วดูเนียนขึ้น**
        eyebrow_resized[:, :, 3] = cv2.GaussianBlur(eyebrow_resized[:, :, 3], (5, 5), 2)

        # **ใช้ Alpha Blending ให้ดูเนียนขึ้น**
        for c in range(3):  # วางเฉพาะช่องสี BGR
            face[left_y_min:left_y_max, left_x_min:left_x_max, c] = np.where(
                eyebrow_resized[:, :, 3] > 50,  # ใช้ Alpha Channel เป็นเงื่อนไข
                cv2.addWeighted(face[left_y_min:left_y_max, left_x_min:left_x_max, c], 0.5, eyebrow_resized[:, :, c], 0.5, 0),  # ใช้การผสมสี
                face[left_y_min:left_y_max, left_x_min:left_x_max, c]  # ใช้ค่าสีของใบหน้า
            )

# บันทึกภาพใบหน้าที่มีคิ้วซ้ายที่วางตรงจุด 285
output_path = "/mnt/data/output_eyebrow_fixed.png"
cv2.imwrite(output_path, face)

# แสดงผลลัพธ์
plt.figure(figsize=(8,6))
plt.imshow(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
plt.axis("off")
plt.title("Face with Fixed Eyebrow")
plt.show()









# import cv2
# import mediapipe as mp
# import numpy as np
# import matplotlib.pyplot as plt

# # โหลดภาพใบหน้า
# image_path = "C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Backend/add_eyebrow/expected_output.png"
# image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

# # แปลงภาพเป็น RGB
# image_rgb = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)

# # โหลดโมเดล Mediapipe Face Mesh
# mp_face_mesh = mp.solutions.face_mesh
# with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5) as face_mesh:
#     results = face_mesh.process(image_rgb)

# # ตรวจสอบว่าพบใบหน้าหรือไม่
# if results.multi_face_landmarks:
#     for face_landmarks in results.multi_face_landmarks:
#         ih, iw, _ = image.shape

#         # หาตำแหน่งคิ้วซ้ายและขวา
#         left_eyebrow = [(face_landmarks.landmark[i].x * iw, face_landmarks.landmark[i].y * ih)
#                         for i in [70, 63, 105, 66, 107]]
#         right_eyebrow = [(face_landmarks.landmark[i].x * iw, face_landmarks.landmark[i].y * ih)
#                          for i in [285]]

#         # คำนวณขอบเขตของคิ้วซ้ายและขวา
#         left_x_min, left_x_max = int(min([p[0] for p in left_eyebrow])), int(max([p[0] for p in left_eyebrow]))
#         left_y_min, left_y_max = int(min([p[1] for p in left_eyebrow])), int(max([p[1] for p in left_eyebrow]))

#         right_x_min, right_x_max = int(min([p[0] for p in right_eyebrow])), int(max([p[0] for p in right_eyebrow]))
#         right_y_min, right_y_max = int(min([p[1] for p in right_eyebrow])), int(max([p[1] for p in right_eyebrow]))

#         # วาดตำแหน่งของคิ้วเพื่อให้แน่ใจว่าถูกต้อง
#         for point in left_eyebrow + right_eyebrow:
#             cv2.circle(image, (int(point[0]), int(point[1])), 3, (0, 255, 0), -1)

# # แสดงผลลัพธ์
# plt.figure(figsize=(8,6))
# plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
# plt.axis("off")
# plt.title("Corrected Eyebrow Position")
# plt.show()
