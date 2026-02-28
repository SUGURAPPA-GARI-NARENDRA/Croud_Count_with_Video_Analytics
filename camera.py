import cv2
import threading

class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.running = True
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

    def get_frame(self):
        return self.frame