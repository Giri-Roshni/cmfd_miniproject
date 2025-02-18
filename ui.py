# manage GUI part and responsiveness
import tkinter as tk
from tkinter import filedialog, Label, Button, Frame
import cv2
from PIL import Image, ImageTk
import os
from detect import Detect
from utils import resize_image, display_image

class ForgeryDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Forgery Detection")
        self.root.geometry("900x700")
        self.root.configure(bg="#2C3E50")
        
        self.image = None
        self.forgery_parts = None
        
        # Responsive Layout
        self.frame = Frame(root, bg="#34495E")
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.label = Label(self.frame, text="Select an image", font=("Arial", 14), bg="#34495E", fg="white")
        self.label.pack(pady=10)
        
        self.choose_button = Button(self.frame, text="Choose Image", command=self.choose_image, font=("Arial", 12), bg="#1ABC9C", fg="white")
        self.choose_button.pack(pady=5)
        
        self.detect_button = Button(self.frame, text="Detect Forgery", command=self.detect_forgery, font=("Arial", 12), bg="#E67E22", fg="white", state=tk.DISABLED)
        self.detect_button.pack(pady=5)
        
        self.image_label = Label(self.frame, bg="#34495E")
        self.image_label.pack(pady=10)
        
        self.result_label = Label(self.frame, text="", font=("Arial", 12), fg="yellow", bg="#34495E")
        self.result_label.pack(pady=10)
        
        self.save_button = Button(self.frame, text="Save Results", command=self.save_results, font=("Arial", 12), bg="#3498DB", fg="white", state=tk.DISABLED)
        self.save_button.pack(pady=5)
    
    def choose_image(self):
        image_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if image_path:
            self.image = cv2.imread(image_path)
            self.image = resize_image(self.image)
            display_image(self.image, self.image_label)
            self.detect_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.DISABLED)
    
    def detect_forgery(self):
        if self.image is not None:
            detect_obj = Detect(self.image)
            detect_obj.siftDetector()
            forgery_image, _, self.forgery_parts = detect_obj.locateForgery()
            
            if forgery_image is not None:
                forgery_image = resize_image(forgery_image)
                display_image(forgery_image, self.image_label)
                parts_text = "\n".join([f"Forgery at: {points}" for points in self.forgery_parts])
                self.result_label.config(text=f"Forgery Detected:\n{parts_text}", fg="yellow")
                self.save_button.config(state=tk.NORMAL)
            else:
                self.result_label.config(text="No forgery detected!", fg="yellow")
    
    def save_results(self):
        if self.image is not None and self.forgery_parts is not None:
            save_dir = filedialog.askdirectory(title="Select Directory to Save Results")
            if save_dir:
                forgery_image_path = os.path.join(save_dir, "forgery_detected.png")
                cv2.imwrite(forgery_image_path, cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
                self.result_label.config(text="Results saved successfully!", fg="yellow")
