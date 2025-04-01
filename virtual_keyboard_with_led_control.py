import cv2
import mediapipe as mp
import pygame
from pyfirmata2 import Arduino, util  
import numpy as np

pygame.init()
screen = pygame.display.set_mode((800, 600))

sounds = {
    "Sa": pygame.mixer.Sound("sa.wav"),
    "Re": pygame.mixer.Sound("re.wav"),
    "Ga": pygame.mixer.Sound("ga.wav"),
    "Ma": pygame.mixer.Sound("ma.wav"),
    "Pa": pygame.mixer.Sound("pa.wav"),
    "Da": pygame.mixer.Sound("da.wav"),
    "Ni": pygame.mixer.Sound("ni.wav")
}

beep_sound = pygame.mixer.Sound("beep.wav")  

keys = ["Sa", "Re", "Ga", "Ma", "Pa", "Da", "Ni"]
key_rects = [pygame.Rect(50 + i * 100, 300, 80, 80) for i in range(len(keys))]

def draw_keys(pressed_keys=None):
    pressed_keys = pressed_keys or []  
    for i, rect in enumerate(key_rects):
        if i in pressed_keys:  
            pygame.draw.rect(screen, (255, 0, 0), rect, 0)
        else:
            pygame.draw.rect(screen, (0, 255, 0), rect, 2)
        text = pygame.font.Font(None, 36).render(keys[i], True, (255, 255, 255))
        screen.blit(text, (rect.x + 20, rect.y + 25))

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

comport = 'COM3'  
board = Arduino(comport)

it = util.Iterator(board)
it.start()

led_pins = [
    board.get_pin('d:6:o'),  # Sa
    board.get_pin('d:7:o'),  # Re
    board.get_pin('d:8:o'),  # Ga
    board.get_pin('d:9:o'), # Ma
    board.get_pin('d:10:o'), # Pa
    board.get_pin('d:11:o'), # Da
    board.get_pin('d:12:o')   # Ni 
]

ir_sensor_pin = board.get_pin('d:3:i')  
ir_led_pin = board.get_pin('d:13:o')    

ir_sensor_pin.enable_reporting()

ir_sensor_state = None

is_beeping = False

def ir_callback(value):
    global ir_sensor_state
    ir_sensor_state = value

ir_sensor_pin.register_callback(ir_callback)

key_states = [False] * len(keys)  

def control_leds(key_index, state):
    if led_pins[key_index] is not None:
        led_pins[key_index].write(state)

heatmap = np.zeros((600, 800), dtype=np.float32)  

decay_factor = 0.98  
intensity_increment_fingertips = 500  
intensity_increment_other_landmarks = 200  


running = True
while running:
    screen.fill((0, 0, 0))
    
    ret, frame = cap.read()
    if not ret:
        break

    flipped_frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    hand_canvas = np.zeros((600, 800, 3), dtype=np.uint8)  

    pressed_keys = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            scaled_landmarks = []
            for lm in hand_landmarks.landmark:
                x, y = int(lm.x * 800), int(lm.y * 600)
                scaled_landmarks.append((x, y))

            for idx, (x, y) in enumerate(scaled_landmarks):
                if 0 <= x < 800 and 0 <= y < 600:
                    if idx in [8, 12, 16, 20]:  
                        heatmap[y, x] += intensity_increment_fingertips
                    else:
                        heatmap[y, x] += intensity_increment_other_landmarks

            for connection in mp_hands.HAND_CONNECTIONS:
                start_idx, end_idx = connection
                start_point = scaled_landmarks[start_idx]
                end_point = scaled_landmarks[end_idx]
                cv2.line(hand_canvas, start_point, end_point, (255, 255, 255), 2)

            for (x, y) in scaled_landmarks:
                cv2.circle(hand_canvas, (x, y), 5, (0, 255, 0), -1)

            fingertip_indices = [8, 12, 16, 20]
            for tip_idx in fingertip_indices:
                fingertip = hand_landmarks.landmark[tip_idx]
                x, y = int(fingertip.x * 800), int(fingertip.y * 600)

                for i, rect in enumerate(key_rects):
                    if rect.collidepoint(x, y):
                        pressed_keys.append(i)  

    for i in range(len(keys)):
        if i in pressed_keys:
            if not key_states[i]: 
                key_states[i] = True
                sounds[keys[i]].play()  
                control_leds(i, 1)     
        else:
            if key_states[i]: 
                key_states[i] = False
                control_leds(i, 0)     

    heatmap *= decay_factor

    heatmap = cv2.GaussianBlur(heatmap, (31, 31), sigmaX=0)  

    heatmap_normalized = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    heatmap_colored = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_JET)  

    cv2.imshow("Heatmap", heatmap_colored)

    hand_canvas_rgb = cv2.cvtColor(hand_canvas, cv2.COLOR_BGR2RGB)  
    hand_surface = pygame.surfarray.make_surface(np.rot90(hand_canvas_rgb))  

    flipped_hand_surface = pygame.transform.flip(hand_surface, True, False)

    screen.blit(flipped_hand_surface, (0, 0))  
    draw_keys(pressed_keys)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if ir_sensor_state is not None:
        if ir_sensor_state == 0: 
            ir_led_pin.write(1)  
            if not is_beeping:  
                beep_sound.play()
                is_beeping = True
        else: 
            ir_led_pin.write(0) 
            is_beeping = False 

    pygame.display.flip()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
pygame.quit()
board.exit()