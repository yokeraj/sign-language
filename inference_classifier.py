import pickle
import cv2
import mediapipe as mp
import numpy as np
import pygame
import random
import time


model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']


cap = cv2.VideoCapture(0)


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.3)


labels_dict = {0: 'Yes', 1: 'No', 2: 'I Love You', 3: 'B', 4: 'G', 5: 'D'}


pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Sign Language Game')
font = pygame.font.SysFont('Arial', 36)


score = 0
time_limit = 10 
game_over = False
game_started = False
gesture_to_match = random.choice(list(labels_dict.values()))  


start_time = time.time()


start_button = pygame.Rect(300, 250, 200, 60)
restart_button = pygame.Rect(300, 350, 200, 60)


def display_text(text, position, color=(255, 255, 255)):
    label = font.render(text, True, color)
    screen.blit(label, position)


def reset_game():
    global score, gesture_to_match, game_over, start_time
    score = 0
    gesture_to_match = random.choice(list(labels_dict.values()))  # New random gesture
    game_over = False
    start_time = time.time()


while True:
    screen.fill((0, 0, 0))  
    frame = None  

    if not game_started:
        
        pygame.draw.rect(screen, (0, 128, 0), start_button)
        display_text("Start", (360, 260))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  
                exit()  
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    game_started = True
                    reset_game()

    else:
        
        if not game_over:
            
            display_text(f"Perform gesture: {gesture_to_match}", (250, 50))

    
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                continue  

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            
            data_aux = []
            x_ = []
            y_ = []

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )

                
                    for landmark in hand_landmarks.landmark:
                        x_ = landmark.x
                        y_ = landmark.y
                        data_aux.append(x_)
                        data_aux.append(y_)

                
                min_x = min(data_aux[0::2])  
                min_y = min(data_aux[1::2])  
                normalized_data = [(data_aux[i] - min_x) if i % 2 == 0 else (data_aux[i] - min_y) for i in range(len(data_aux))]

                
                prediction = model.predict([np.asarray(normalized_data)])
                predicted_character = labels_dict[int(prediction[0])]

                
                display_text(f"Detected: {predicted_character}", (250, 120))

                
                if predicted_character == gesture_to_match:
                    score += 1  
                    gesture_to_match = random.choice(list(labels_dict.values()))
                    start_time = time.time()  

            
            elapsed_time = time.time() - start_time

            
            display_text(f"Time left: {max(0, int(time_limit - elapsed_time))}s", (650, 20))

            if elapsed_time > time_limit:
                game_over = True  

    
            display_text(f"Score: {score}", (20, 20))

        else:
            
            display_text("Game Over!", (320, 200), (255, 0, 0))

            
            pygame.draw.rect(screen, (128, 0, 0), restart_button)
            display_text("Restart", (350, 360))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.collidepoint(event.pos):
                        reset_game()

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    
    pygame.display.flip()

    
    if game_started and frame is not None:
        cv2.imshow('Camera Feed', frame)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
