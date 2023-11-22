import cv2
import mediapipe as mp
import numpy as np
import time
import random
import sys

from lib.pyVector import Vector
from lib.Object import CircleObject
from lib.Puck import Puck

# Initialize webcam
#1

cap=cv2.VideoCapture(0)

success, frame=cap.read() # just to get frame dim
height, width, _ = frame.shape


# Initialize hand tracking
#2

mp_hands = mp.solutions.mediapipe.python.solutions.hands

hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,
                       min_detection_confidence=0.75,
                       min_tracking_confidence=0.75)

# Initialize paddle and puck positions
#3

def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    return (r, g, b)

TARGET_SIDE = 30
PADDLE_COLOR = random_color()
PADDLE_RADIUS = 25
PUCK_COLOR = random_color()
PUCK_RADIUS = 10
PUCK_SPEED = 200
NO_OF_TARGETS = 5

init_pos = Vector(random.random() * width, random.random() * height)

init_velocity = Vector(random.random(), random.random()).normalized()

puck = Puck(init_pos, PUCK_RADIUS, init_velocity, PUCK_SPEED, frame)


# Load target image and resize it to 30,30
#4

img = cv2.imread('Media/target.png')
img = cv2.resize(img, (TARGET_SIDE, TARGET_SIDE))

# Initialize 5 target positions randomly(remember assignment 2!!)
#5

donut_obj_l = []
for _ in range(NO_OF_TARGETS):
    _x = random.random() * width
    _y = random.random() * height

    donut_obj_l.append(CircleObject(Vector(_x, _y), TARGET_SIDE/np.sqrt(2)))


# Initialize score
#6

GAME_TEXT_SIZE = 1
END_GAME_TEXT_SIZE = 5

score = 0
targets_destroyed = 0

game_over = False
has_won = False

# Initialize timer variables
start_time = time.time()
GAME_DURATION = 30  # 1/2 minute in seconds
time.sleep(0.05)
old_time = start_time

while True:
    # Calculate remaining time and elapsed time in minutes and seconds   
    #9

    time_diff = time.time() - old_time
    old_time = time.time()
    fps = 1/time_diff
    
    # Read a frame from the webcam
    #10
    
    success, frame=cap.read()

    # Flip the frame horizontally for a later selfie-view display
    #11

    frame = cv2.flip(frame, 1) # flipping the image cuz by default, it shows a mirror of the real world

    # Convert the BGR image to RGB
    #12

    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with mediapipe hands
    #13

    result = hands.process(frameRGB)
    
    hand_land_mark = result.multi_hand_landmarks  # hand land marks

    if hand_land_mark:  # hand on screen
        for handLM in hand_land_mark:
            for id, lm in enumerate(handLM.landmark):

                if id == 8:  # 8th index in the array refers to tip of index finger

                    index_pos = Vector(lm.x * width, lm.y * height)

                    # Update paddle position based on index finger tip
                    #14

                    paddle = CircleObject(index_pos, PADDLE_RADIUS)
                    paddle.render(frame, PADDLE_COLOR)
                    # cv2.circle(frame, (index_pos.x, index_pos.y), 25, (255, 0, 255), -1) # (image, pos, radius, color, thickness)

                    # position of index finger (scaled to be from -1 to 1)

    else:
        paddle = CircleObject(Vector(10000, 10000), PADDLE_RADIUS)


    # Update puck position based on its velocity
    #15

    puck.update_n_render(frame, fps, PUCK_COLOR)

    # puck.render(frame, PUCK_COLOR)

    # Check for collisions with the walls
    #16

    # done in puck script

    # Check for collisions with the paddle
    #17

    if(paddle.has_collided(puck.circle_object)):

        normal = (puck.position - paddle.position).normalized()
        incident = puck.velocity
        reflected_velocity = incident - normal*float(2*(np.dot((incident.x, incident.y), (normal.x, normal.y))))

        puck.position = paddle.position + normal*(paddle.radius+puck.radius)
        puck.velocity = reflected_velocity
        puck.update_n_render(frame, fps, PUCK_COLOR)


    # Check for collisions with the targets(use is_within_acceptance)    
    #18
    
    for obj in donut_obj_l:
        if obj.has_collided(puck.circle_object) and not obj.destroyed and not game_over:
            obj.destroyed = True
            score += 1
            targets_destroyed += 1
            puck.speed += 10 # made it increase by 10 instead of 2 cuz too slow

    # Draw paddle, puck, and targets on the frame and overlay target image on frame
    #19

        obj.image(frame, img)

    # Display the player's score on the frame
    #20

    if not game_over:
        cv2.putText(frame, f"Score: {score}", (0, 25), cv2.FONT_HERSHEY_SIMPLEX, GAME_TEXT_SIZE, (255, 255, 255))

    # Display the remaining time on the frame
    #21

    if not game_over:
        cv2.putText(frame, f"Time left: {GAME_DURATION - int(time.time() - start_time)}", (0, 55), cv2.FONT_HERSHEY_SIMPLEX, GAME_TEXT_SIZE, (255, 255, 255))
    else:
        cv2.putText(frame, "Time left: 0", (0, 55), cv2.FONT_HERSHEY_SIMPLEX, GAME_TEXT_SIZE, (255, 255, 255))


    # Check if all targets are hit or time is up
    #22

    if (targets_destroyed == NO_OF_TARGETS):
        game_over = True
        has_won = True
        cv2.putText(frame, f"YOU WON", (int(width/2 - 300), int(height/2 - END_GAME_TEXT_SIZE*25/2)), cv2.FONT_HERSHEY_SIMPLEX, END_GAME_TEXT_SIZE, (255, 255, 255))
        cv2.putText(frame, f" Score: {score}", (int(width/2 - 300), int(height/2 + END_GAME_TEXT_SIZE*25/2)), cv2.FONT_HERSHEY_SIMPLEX, END_GAME_TEXT_SIZE, (255, 255, 255))
    
    if (GAME_DURATION - int(time.time() - start_time)) <= 0:
        game_over = True
        cv2.putText(frame, "TIME'S UP", (int(width/2 - 300), int(height/2 + END_GAME_TEXT_SIZE*25/2)), cv2.FONT_HERSHEY_SIMPLEX, END_GAME_TEXT_SIZE, (255, 255, 255))

    # Display the resulting frame
    #23

    cv2.imshow("Video", frame)

    # Exit the game when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
#24

sys.exit()
