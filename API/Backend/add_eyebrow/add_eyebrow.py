import cv2
import mediapipe as mp

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# โหลดรูปภาพ
image = cv2.imread("C:/Users/Chits/Documents/pensook/Github/Website_DEEPBROW/API/Backend/add_eyebrow/expected_output.png")
if image is None:
    print("Error: ไม่พบไฟล์ภาพ")
    exit()

# แปลงสีเป็น RGB
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# ใช้งาน Face Mesh
with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
    results = face_mesh.process(image_rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx in [70, 63, 105, 66, 107]:  # จุดของคิ้ว (ปรับแต่งได้)
                landmark = face_landmarks.landmark[idx]
                ih, iw, _ = image.shape
                x, y = int(landmark.x * iw), int(landmark.y * ih)
                cv2.circle(image, (x, y), 3, (0, 255, 0), -1)

# แสดงผลลัพธ์
cv2.imshow("Eyebrow Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
