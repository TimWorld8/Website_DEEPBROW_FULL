import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Load the images
face_image_path = 'remove_eyebrow/expected_output.png'
eyebrow_image_path = 'add_eyebrow/pngtree-realistic-eyebrows-png-image_7572667.png'
face_image = cv2.imread(face_image_path)
eyebrow_image = cv2.imread(eyebrow_image_path, cv2.IMREAD_UNCHANGED)  # Load with alpha channel

# Convert the BGR image to RGB
face_image_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

# Process the image and detect face mesh
with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5) as face_mesh:
    results = face_mesh.process(face_image_rgb)

    # Check if landmarks are detected
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Get the coordinates of landmark 285
            h, w, _ = face_image.shape
            x = int(face_landmarks.landmark[285].x * w)
            y = int(face_landmarks.landmark[285].y * h)

            # Resize eyebrow image to fit the face
            eyebrow_width = int(w * 0.2)  # Adjust size as needed
            eyebrow_height = int(eyebrow_image.shape[0] * (eyebrow_width / eyebrow_image.shape[1]))
            resized_eyebrow = cv2.resize(eyebrow_image, (eyebrow_width, eyebrow_height))

            # Overlay the eyebrow image
            for i in range(resized_eyebrow.shape[0]):
                for j in range(resized_eyebrow.shape[1]):
                    if resized_eyebrow[i, j, 3] > 0:  # Check alpha channel
                        face_image[y + i, x + j] = resized_eyebrow[i, j, :3]

# Save the output image
output_path = 'remove_eyebrow/face_with_eyebrow.png'
cv2.imwrite(output_path, face_image)

# Display the output image
cv2.imshow('Face with Eyebrow', face_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
