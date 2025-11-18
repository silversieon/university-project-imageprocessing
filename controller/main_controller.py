from PyQt5.QtWidgets import QFileDialog, QMessageBox
from model.image_processor import VideoProcessor

class MainController:
    def __init__(self, view):
        self.view = view
        self.model = VideoProcessor()

        # connect buttons to actions
        self.view.open_btn.clicked.connect(self.open_image)
        self.view.gray_btn.clicked.connect(self.convert_gray)

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(filter="Images (*.png *.jpg *.jpeg)")
        if not path:
            return
        img = self.model.load(path)
        if img is None:
            QMessageBox.warning(self.view, "Load failed", f"Failed to load image:\n{path}")
            return
        self.view.display_image(img)

    def convert_gray(self):
        img = self.model.to_gray()
        if img is not None:
            self.view.display_image(img)
