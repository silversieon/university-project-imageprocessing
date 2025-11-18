import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        self.image = None

    def load(self, path: str):
        """Load image from path. Use numpy.fromfile + cv2.imdecode to support
        Windows paths containing non-ASCII characters (cv2.imread may fail).
        Returns the image array or None on failure."""
        try:
            data = np.fromfile(path, dtype=np.uint8)
            if data.size == 0:
                self.image = None
                return None
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)
            self.image = img
            return img
        except Exception:
            self.image = None
            return None

    def to_gray(self):
        if self.image is None:
            return None
        return cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
