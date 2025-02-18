# contains detect class for image forgery detction
import cv2
import numpy as np
from sklearn.cluster import DBSCAN

class Detect:
    def __init__(self, image):
        self.image = image
    
    def siftDetector(self):
        """Apply SIFT feature detection."""
        sift = cv2.SIFT_create()
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.key_points, self.descriptors = sift.detectAndCompute(gray, None)
        return self.key_points, self.descriptors
    
    def locateForgery(self, eps=40, min_sample=2):
        """Identify potential copy-move forgery regions."""
        if self.descriptors is None:
            return None, None, None

        clusters = DBSCAN(eps=eps, min_samples=min_sample).fit(self.descriptors)
        labels = clusters.labels_
        unique_labels = np.unique(labels)
        
        if len(unique_labels) == 1 and unique_labels[0] == -1:
            return None, None, None  # No forgery detected

        forgery = self.image.copy()
        non_forgery = self.image.copy()
        
        clusters_dict = {label: [] for label in unique_labels if label != -1}
        
        for idx, label in enumerate(labels):
            if label != -1:
                clusters_dict[label].append(
                    (int(self.key_points[idx].pt[0]), int(self.key_points[idx].pt[1]))
                )
        
        forgery_parts = []
        for points in clusters_dict.values():
            if len(points) > 1:
                forgery_parts.append(points)
                for i in range(1, len(points)):
                    cv2.line(forgery, points[0], points[i], (0, 255, 0), 3)
                    cv2.circle(non_forgery, points[i], 5, (0, 0, 255), -1)
                    cv2.putText(forgery, "Copied", points[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    cv2.putText(non_forgery, "Original", points[i], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return forgery, non_forgery, forgery_parts
