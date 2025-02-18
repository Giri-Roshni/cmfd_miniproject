# helper function like resizing and displaying images.
import cv2
from PIL import Image, ImageTk

def resize_image(image, max_width=600, max_height=600):
    """Resize image while maintaining aspect ratio."""
    h, w, _ = image.shape
    scale_factor = min(max_width / w, max_height / h, 1)
    if scale_factor < 1:
        image = cv2.resize(image, (int(w * scale_factor), int(h * scale_factor)))
    return image

def display_image(image, label):
    """Convert OpenCV image to Tkinter-compatible format and display."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)
    image_tk = ImageTk.PhotoImage(image_pil)
    label.config(image=image_tk)
    label.image = image_tk
