import cv2
import numpy as np
from .pyVector import Vector

# Base class for all circular objects
class CircleObject:

    def __init__(self, origin: Vector, radius: int):
        self.position = Vector(origin.x, origin.y)
        self.radius = radius
        self.destroyed = False

    # checks collision with other circular objects
    def has_collided(self, target) -> bool:

        diff_magnitude = (Vector(target.position.x, target.position.y) - Vector(self.position.x, self.position.y)).magnitude()
        return diff_magnitude <= (target.radius + self.radius)
    
    # renders basic circle
    def render(self, frame, color: tuple):
        cv2.circle(frame, (int(self.position.x), int(self.position.y)), self.radius, color, -1)

    # renders image instead of circle
    def image(self, frame, img):
        height, width, _ = img.shape
        f_height, f_width, _ = frame.shape

        self.position.x = np.clip(self.position.x, (width/2), (f_width - width/2))
        self.position.y = np.clip(self.position.y, (height/2), (f_height - height/2))
        
        top_left = Vector(int(self.position.x) - int(width/2), int(self.position.y) + int(height/2))
        bottom_right = Vector(int(self.position.x) + int(width/2), int(self.position.y) - int(height/2))
        

        if not self.destroyed:
            frame[bottom_right.y:top_left.y, top_left.x:bottom_right.x, :] = img
            




