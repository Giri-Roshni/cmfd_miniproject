import cv2
import numpy as np
from sklearn.cluster import DBSCAN
import tkinter as tk
from tkinter import filedialog, Label, Button, Frame
from PIL import Image, ImageTk
import os

class Detect:
    def __init__(self, image):
        self.image = image
    
    def siftDetector(self):
        sift = cv2.SIFT_create()
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.key_points, self.descriptors = sift.detectAndCompute(gray, None)
        return self.key_points, self.descriptors
    
    def locateForgery(self, eps=40, min_sample=2):
        clusters = DBSCAN(eps=eps, min_samples=min_sample).fit(self.descriptors)
        size = np.unique(clusters.labels_).shape[0] - 1
        forgery = self.image.copy()
        non_forgery = self.image.copy()
        
        if size == 0 and np.unique(clusters.labels_)[0] == -1:
            return None, None, None
        
        size = max(size, 1)
        cluster_list = [[] for _ in range(size)]
        for idx, label in enumerate(clusters.labels_):
            if label != -1:
                cluster_list[label].append(
                    (int(self.key_points[idx].pt[0]), int(self.key_points[idx].pt[1]))
                )
        
        forgery_parts = []
        for points in cluster_list:
            if len(points) > 1:
                forgery_parts.append(points)
                for idx1 in range(1, len(points)):
                    cv2.line(forgery, points[0], points[idx1], (0, 255, 0), 3)
                    cv2.circle(non_forgery, points[idx1], 5, (0, 0, 255), -1)
                    cv2.putText(forgery, "Copied", points[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.putText(non_forgery, "Original", points[idx1], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return forgery, non_forgery, forgery_parts

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
        
        self.detect_button = Button(self.frame, text="Detect Forgery", command=self.detect_forgery, font=("Arial", 12), bg="#E67E22", fg="white", state=tk.DISABLED)
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
            self.image = cv2.imread(image_path)
            self.image = self.resize_image(self.image)
            self.display_image(self.image)
            self.detect_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.DISABLED)
    
    def resize_image(self, image, max_width=800, max_height=600):
        h, w, _ = image.shape
        scale_factor = min(max_width / w, max_height / h, 1)
        if scale_factor < 1:
            image = cv2.resize(image, (int(w * scale_factor), int(h * scale_factor)))
        return image
    
    def display_image(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)
        self.image_label.config(image=image_tk)
        self.image_label.image = image_tk
    
    def detect_forgery(self):
        if self.image is not None:
            detect_obj = Detect(self.image)
            detect_obj.siftDetector()
            forgery_image, non_forgery_image, self.forgery_parts = detect_obj.locateForgery()
            
            if forgery_image is not None:
                forgery_image = self.resize_image(forgery_image)
                self.display_image(forgery_image)
                parts_text = "\n".join([f"Forgery cluster at: {points}" for points in self.forgery_parts])
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
                
                forgery_details_path = os.path.join(save_dir, "forgery_details.txt")
                with open(forgery_details_path, "w") as f:
                    for idx, points in enumerate(self.forgery_parts):
                        f.write(f"Cluster {idx + 1}: {points}\n")
                
                self.result_label.config(text="Results saved successfully!", fg="yellow")

if __name__ == "__main__":
    root = tk.Tk()
    app = ForgeryDetectionApp(root)
    root.mainloop()
