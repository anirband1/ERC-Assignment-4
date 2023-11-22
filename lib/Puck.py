from .pyVector import Vector
from .Object import CircleObject

class Puck:

    def __init__(self, position: Vector, radius: int, velocity_dir: Vector, speed: int, frame) -> None:
        self.position = position
        self.velocity = velocity_dir
        self.radius = radius
        self.speed = speed
        self.circle_object = CircleObject(self.position, self.radius)
        
        self.can_collide_with_paddle = True
        height, width, _ = frame.shape
        self.FRAME_WIDTH = width
        self.FRAME_HEIGHT = height


    def update_n_render(self, frame, fps, color):

        self.circle_object = CircleObject(self.position, self.radius)

        # UPDATE 

        time_elapsed = 1/fps

        # check collisions (basic AABB collisions) for walls

        if self.position.x <= self.radius/2 :
            self.position.x = self.radius/2
            self.velocity.x = -self.velocity.x

        if self.position.x >= self.FRAME_WIDTH - self.radius/2:
            self.position.x = self.FRAME_WIDTH - self.radius/2
            self.velocity.x = -self.velocity.x

        if self.position.y <= self.radius/2 :
            self.position.y = self.radius/2
            self.velocity.y = -self.velocity.y

        if self.position.y >= self.FRAME_HEIGHT - self.radius/2:
            self.position.y = self.FRAME_HEIGHT - self.radius/2
            self.velocity.y = -self.velocity.y

        self.position = self.position + self.velocity * time_elapsed * self.speed


        # RENDER

        # self.circle_object.render(frame, color)
        self.circle_object.render(frame, color)




