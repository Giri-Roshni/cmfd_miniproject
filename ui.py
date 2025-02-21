import tkinter as tk
from tkinter import filedialog, Label, Button, Frame
import os
import cv2
from detect import Detect
from utils import resize_image, display_image



class ForgeryDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Copy-Move Forgery Detection")
        self.root.geometry("900x700")
        self.root.configure(bg="#2C3E50")
        
        self.image = None
        self.forgery_parts = None
        
        self.frame = Frame(root, bg="#34495E")
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.label = Label(self.frame, text="Select an image to detect forgery", font=("Arial", 14), bg="#34495E", fg="white")
        self.label.pack(pady=10)
        
        self.choose_button = Button(self.frame, text="Choose Image", command=self.choose_image, font=("Arial", 12), bg="#1ABC9C", fg="white")
        self.choose_button.pack(pady=5)
        
        self.detect_button = Button(self.frame, text="Detect Forgery", command=self.detect_forgery, font=("Arial", 12), bg="#E67E22", fg="black", state=tk.DISABLED)
        self.detect_button.pack(pady=5)
        
        self.image_label = Label(self.frame, bg="#34495E")
        self.image_label.pack(pady=10)
        
        self.result_label = Label(self.frame, text="", font=("Arial", 12), fg="green", bg="#34495E")
        self.result_label.pack(pady=10)
        
        self.save_button = Button(self.frame, text="Save Results", command=self.save_results, font=("Arial", 12), bg="#3498DB", fg="white", state=tk.DISABLED)
        self.save_button.pack(pady=5)
    
    def choose_image(self):
        image_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if image_path:
            # Clear the previous result
            self.clear_previous_result()

            self.image = cv2.imread(image_path)
            self.image = resize_image(self.image)
            display_image(self.image, self.image_label)
            self.detect_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.DISABLED)
    
    def clear_previous_result(self):
        self.forgery_parts = None
        self.result_label.config(text="", fg="green")
        self.image_label.config(image='', text='')  # Clear the displayed image
        
    def detect_forgery(self):
        if self.image is not None:
            detect_obj = Detect(self.image)
            detect_obj.siftDetector()
            forgery_image, non_forgery_image, self.forgery_parts = detect_obj.locateForgery()
            
            if forgery_image is not None:
                forgery_image = resize_image(forgery_image)
                display_image(forgery_image, self.image_label)
                # parts_text = "\n".join([f"Forgery cluster at: {points}" for points in self.forgery_parts])
                self.result_label.config(text=f"Forgery Detected", fg="Red")
                self.save_button.config(state=tk.NORMAL)
            else:
                self.result_label.config(text="No forgery detected!", fg="Yellow")
    
    def save_results(self):
        if self.image is not None and self.forgery_parts is not None:
            save_dir = filedialog.askdirectory(title="Select Directory to Save Results")
            if save_dir:
                forgery_image_path = os.path.join(save_dir, "forgery_detected.png")
                cv2.imwrite(forgery_image_path, cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
                
                forgery_details_path = os.path.join(save_dir, "forgery_details.txt")
                with open(forgery_details_path, "w") as f:
                    for idx, points in enumerate(self.forgery_parts):
                        f.write(f"Cluster {idx + 1}: {points}\n")
                
                self.result_label.config(text="Results saved successfully!", fg="yellow")


    