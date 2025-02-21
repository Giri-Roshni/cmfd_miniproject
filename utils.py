import cv2
from PIL import Image, ImageTk

def resize_image(image, max_width=800, max_height=400):
    """
    Resizes an image to fit within the specified maximum width and height while maintaining aspect ratio.
    Handles both grayscale and color images.
    """
    if len(image.shape) == 2:  # Grayscale image (binary mask)
        h, w = image.shape
    else:  # Color image
        h, w, _ = image.shape
    
    scale_factor = min(max_width / w, max_height / h, 1)
    if scale_factor < 1:
        new_size = (int(w * scale_factor), int(h * scale_factor))
        image = cv2.resize(image, new_size)
    return image

def display_image(image, label):
    """
    Displays an image in a Tkinter label.
    Handles both grayscale and color images.
    """
    if len(image.shape) == 2:  # Grayscale image (binary mask)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)  # Convert grayscale to RGB for display
    else:  # Color image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    image_pil = Image.fromarray(image_rgb)
    image_tk = ImageTk.PhotoImage(image_pil)
    label.config(image=image_tk)
    label.image = image_tk