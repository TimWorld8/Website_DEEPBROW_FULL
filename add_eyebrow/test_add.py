import cv2
import numpy as np

def add_new_eyebrows(image_path, eyebrow_image_path, position):
    # Load the original image
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"Input image not found at: {image_path}")
    
    # Load the new eyebrow image
    eyebrow_image = cv2.imread(eyebrow_image_path, cv2.IMREAD_UNCHANGED)
    if eyebrow_image is None:
        raise FileNotFoundError(f"Eyebrow image not found at: {eyebrow_image_path}")
    
    # Extract the alpha mask from the eyebrow image
    if eyebrow_image.shape[2] == 4:  # Check if the image has an alpha channel
        alpha_mask = eyebrow_image[:, :, 3] / 255.0
        eyebrow_image = eyebrow_image[:, :, :3]  # Remove the alpha channel for blending
    else:
        raise ValueError("Eyebrow image must have an alpha channel for transparency.")
    
    # Calculate size based on the bounding box and add 20 pixels to each dimension
    plus = 5
    x1, y1, x2, y2 = position
    x1 -= plus
    #y1 -= plus
    #x2 += plus
    y2 += plus
    size = (x2 - x1, y2 - y1)
    
    # Resize the eyebrow image to the desired size
    resized_eyebrow = cv2.resize(eyebrow_image, size)
    resized_alpha_mask = cv2.resize(alpha_mask, size)
    
    # Define the region of interest (ROI) in the original image
    roi = image[y1:y2, x1:x2]
    
    # Blend the new eyebrow with the ROI
    for c in range(0, 3):
        roi[:, :, c] = (resized_alpha_mask * resized_eyebrow[:, :, c] + (1 - resized_alpha_mask) * roi[:, :, c])
    
    # Place the blended ROI back into the original image
    image[y1:y2, x1:x2] = roi
    
    return image

# Example usage
if __name__ == '__main__':
    input_image_path = 'remove_eyebrow\expected_output.png'
    eyebrow_image_path = 'add_eyebrow\pngtree-realistic-eyebrows-png-image_7572667.png'
    position = (307, 106, 372, 134)  # Original position as (x1, y1, x2, y2)
    
    result_image = add_new_eyebrows(input_image_path, eyebrow_image_path, position)
    cv2.imwrite('add_eyebrow\output_with_new_eyebrows.png', result_image)
    print("New eyebrows added and saved to 'output_with_new_eyebrows.png'")