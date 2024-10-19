import cv2
import mediapipe as mp
import math
import random

import pygame
from pygame import mixer
pygame.init()

screen = pygame.display.set_mode((1200, 800))
background = pygame.image.load('background1.png')

pygame.display.set_caption("Bhektors")
icon = pygame.image.load('logo.png')
pygame.display.set_icon(icon)


pygame.mixer.pre_init(44100,16,2,4096)
pygame.mixer.music.load("backgroundm1.mp3")
pygame.mixer.music.set_volume(0.03)
pygame.mixer.music.play(-1)



mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def is_thumbs_up(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

    return thumb_tip.y < index_tip.y and thumb_tip.y < middle_tip.y and \
           thumb_tip.y < ring_tip.y and thumb_tip.y < pinky_tip.y


def is_thumbs_down(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    return thumb_tip.y > wrist.y


def is_palm_at_rest(hand_landmarks):

    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    return abs(wrist.y - thumb_tip.y) < 50 and abs(wrist.y - pinky_tip.y) < 50


def is_index_up(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    return index_tip.y < thumb_tip.y and index_tip.y < middle_tip.y and \
           index_tip.y < ring_tip.y and index_tip.y < pinky_tip.y

def is_v_sign(hand_landmarks):
  thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
  index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
  middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
  ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
  pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
  return (index_tip.y < thumb_tip.y and index_tip.y < ring_tip.y) and \
         (middle_tip.y < thumb_tip.y and middle_tip.y < ring_tip.y) and \
         (thumb_tip.y < ring_tip.y and thumb_tip.y < pinky_tip.y)


playerImg = pygame.image.load('player1.png')
playerX = 500
playerY = 520
playerX_change = 0

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 3
enemy_image_path = pygame.image.load('enemy1.png')
new_width = 100
new_height = 130  
enemy_character_image = pygame.transform.scale(enemy_image_path, (new_width, new_height))
for i in range(num_of_enemies):
    enemyImg.append(enemy_character_image)
    enemyX.append(random.randint(0, 1000))
    enemyY.append(random.randint(50, 300))
    enemyX_change.append(4)
    enemyY_change.append(110)

# Bullet , Ready 
bullet_image_path = pygame.image.load('bullet1.png')
bullet_new_width = 25
bullet_new_height = 25
bullet_character_image = pygame.transform.scale(bullet_image_path, (bullet_new_width, bullet_new_height))

bulletImg = bullet_character_image
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 4
bullet_state = "ready"

score_value = 0
font = pygame.font.Font('freesansbold.ttf', 36)

textX = 10
testY = 10

over_font1 = pygame.font.Font('freesansbold.ttf', 64)
over_font2 = pygame.font.Font('freesansbold.ttf', 26)


def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def game_over_text():
    over_text = over_font1.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (400, 390))

def credit():
    over_text = over_font2.render("~TEAM BHAKTORS", True, (255, 255, 255))
    screen.blit(over_text, (530, 448))


player_image_path = pygame.image.load('player1.png')
player_new_width = 140
player_new_height = 170
player_character_image = pygame.transform.scale(player_image_path, (player_new_width, player_new_height))



def player(x, y):
    screen.blit(player_character_image,(x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 43, y + 10))


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt(math.pow(enemyX - bulletX, 2) + (math.pow(enemyY+6 - bulletY, 2)))
    if distance < 35:
        return True
    else:
        return False
    


IMAGE_FILES = []

cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                screen.fill((0, 0, 0)) 
                screen.blit(background, (0, -110))
                
                
                if is_thumbs_up(hand_landmarks):
                    print("Thumbs up detected!")
                    if bullet_state == "ready":
                        bulletSound = mixer.Sound("cannon.mp3")
                        bulletSound.play()
                        bulletX = playerX
                        fire_bullet(bulletX, bulletY)
                
                elif not is_index_up(hand_landmarks) and  is_v_sign(hand_landmarks):
                    print("v sign detected")
                    playerX_change = 6
                elif is_index_up(hand_landmarks):
                    playerX_change = -6
                
                elif is_palm_at_rest(hand_landmarks):
                    print("Palm at rest detected!")
                    playerX_change = 0
                

                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
            playerX += playerX_change
            if playerX <= 0:
                playerX = 0
            elif playerX >= 1100:
                playerX = 1100


            for i in range(num_of_enemies):

                if enemyY[i] > 380:
                    for j in range(num_of_enemies):
                        enemyY[j] = 2000
                    game_over_text()
                    credit()
                    break

                enemyX[i] += enemyX_change[i]
                if enemyX[i] <= 0:
                    enemyX_change[i] = 4
                    enemyY[i] += enemyY_change[i]
                elif enemyX[i] >= 1100:
                    enemyX_change[i] = -4
                    enemyY[i] += enemyY_change[i]

                collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
                if collision:
                    explosionSound = mixer.Sound("explosion.wav")
                    explosionSound.play()
                    bulletY = 480
                    bullet_state = "ready"
                    score_value += 1
                    enemyX[i] = random.randint(0, 1100)
                    enemyY[i] = random.randint(30, 120)

                enemy(enemyX[i], enemyY[i], i)
                if bulletY <= 0:
                    bulletY = 480
                    bullet_state = "ready"

                if bullet_state == "fire":
                    fire_bullet(bulletX, bulletY)
                    bulletY -= bulletY_change



            player(playerX, playerY)
            show_score(textX, testY)
            pygame.display.update()
        # Flip the image horizontally
        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()