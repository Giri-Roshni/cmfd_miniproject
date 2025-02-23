import cv2
import numpy as np
from sklearn.cluster import DBSCAN

class Detect:
    def __init__(self, image):
        self.image = image
    
    def siftDetector(self):
        """
        Detects key points and descriptors using the SIFT algorithm.
        """
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
            return None, None, None, None, None
        
        size = max(size, 1)
        cluster_list = [[] for _ in range(size)]
        forgery_descriptors = []

        for idx, label in enumerate(clusters.labels_):
            if label != -1:
                cluster_list[label].append(
                    (int(self.key_points[idx].pt[0]), int(self.key_points[idx].pt[1]))
                )
                forgery_descriptors.append(self.descriptors[idx])  # Store descriptors of forgery regions
        
        forgery_parts = []
        binary_mask = np.zeros_like(cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY))
        
        for points in cluster_list:
            if len(points) > 1:
                forgery_parts.append(points)
                for idx1 in range(1, len(points)):
                    cv2.line(forgery, points[0], points[idx1], (200, 120, 100), 2)
                    cv2.circle(non_forgery, points[idx1], 5, (0, 0, 255), -1)
                    cv2.putText(forgery, "Copied", points[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    cv2.putText(forgery, "Original", points[idx1], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    cv2.putText(non_forgery, "Original", points[idx1], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    
                    cv2.circle(binary_mask, points[0], 10, 255, -1)
                    cv2.circle(binary_mask, points[idx1], 10, 255, -1)
    
        return forgery, non_forgery, forgery_parts, binary_mask, np.array(forgery_descriptors)
