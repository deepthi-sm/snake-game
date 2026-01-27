import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()

# ---------------- SETTINGS ----------------
WIDTH, HEIGHT = 600, 400
CELL = 20
BASE_SPEED = 8
MAX_SPEED = 20

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (40, 40, 40)

SKINS = [
    {"name": "Classic Green", "color": (0, 255, 0)},
    {"name": "Blue Snake", "color": (0, 150, 255)},
    {"name": "Purple Snake", "color": (180, 0, 255)}
]

BG_MUSIC = [
    "sounds/bg1.wav",
    "sounds/bg2.wav",
    "sounds/bg3.wav"
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 56)

HIGH_SCORE_FILE = "highscore.txt"

# ---------------- SAFE SOUND ----------------
def safe_music_load(path):
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Music load failed:", e)

def safe_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception as e:
        print("Sound load failed:", e)
        return None

EAT_SOUND = safe_sound("sounds/eat.wav")
GAME_OVER_SOUND = safe_sound("sounds/game_over.wav")

# ---------------- UTIL ----------------
def draw_grid():
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read())
    except:
        return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))

# ---------------- START MENU ----------------
def start_menu():
    selected_music = 0
    selected_skin = 0

    while True:
        screen.fill(BLACK)

        title = big_font.render("SNAKE GAME", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        screen.blit(font.render("Press P or ENTER to Play", True, WHITE),
                    (WIDTH//2 - 120, 90))

        screen.blit(font.render("Background Music", True, WHITE), (80, 140))
        for i in range(3):
            color = (0, 255, 0) if i == selected_music else (180, 180, 180)
            prefix = "-> " if i == selected_music else "  "
            screen.blit(font.render(f"{prefix}{i+1}. Track {i+1}", True, color),
                        (100, 170 + i * 30))

        screen.blit(font.render("Snake Skin", True, WHITE), (350, 140))
        for i, skin in enumerate(SKINS):
            color = (0, 255, 0) if i == selected_skin else (180, 180, 180)
            prefix = "-> " if i == selected_skin else "  "
            screen.blit(font.render(f"{prefix}{skin['name']}", True, color),
                        (370, 170 + i * 30))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_p, pygame.K_RETURN):
                    return selected_music, selected_skin
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    selected_music = event.key - pygame.K_1
                if event.key == pygame.K_s:
                    selected_skin = (selected_skin + 1) % len(SKINS)

# ---------------- GAME LOOP ----------------
def game_loop(bg_music_path, skin_color):
    safe_music_load(bg_music_path)

    snake = [(100, 100)]
    direction = (CELL, 0)
    food = (random.randrange(0, WIDTH, CELL),
            random.randrange(0, HEIGHT, CELL))
    score = 0

    while True:
        clock.tick(min(BASE_SPEED + score * 0.3, MAX_SPEED))
        screen.fill(BLACK)
        draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, CELL):
                    direction = (0, -CELL)
                elif event.key == pygame.K_DOWN and direction != (0, -CELL):
                    direction = (0, CELL)
                elif event.key == pygame.K_LEFT and direction != (CELL, 0):
                    direction = (-CELL, 0)
                elif event.key == pygame.K_RIGHT and direction != (-CELL, 0):
                    direction = (CELL, 0)

        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        if (head[0] < 0 or head[0] >= WIDTH or
            head[1] < 0 or head[1] >= HEIGHT or
            head in snake):
            pygame.mixer.music.stop()
            if GAME_OVER_SOUND:
                GAME_OVER_SOUND.play()
            return score

        snake.insert(0, head)

        if head == food:
            score += 1
            if EAT_SOUND:
                EAT_SOUND.play()
            food = (random.randrange(0, WIDTH, CELL),
                    random.randrange(0, HEIGHT, CELL))
        else:
            snake.pop()

        for block in snake:
            pygame.draw.rect(screen, skin_color, (*block, CELL, CELL))

        pygame.draw.rect(screen, RED, (*food, CELL, CELL))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        pygame.display.update()

# ---------------- GAME OVER ----------------
def game_over_screen(score):
    high = load_high_score()
    if score > high:
        save_high_score(score)
        high = score

    while True:
        screen.fill(BLACK)
        screen.blit(big_font.render("GAME OVER", True, RED), (180, 120))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (240, 190))
        screen.blit(font.render(f"High Score: {high}", True, WHITE), (210, 220))

        screen.blit(font.render("R - Restart", True, WHITE), (220, 260))
        screen.blit(font.render("M - Main Menu", True, WHITE), (220, 290))
        screen.blit(font.render("Q - Quit", True, WHITE), (220, 320))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True      # restart game
                if event.key == pygame.K_m:
                    return False     # go back to menu
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


# ---------------- MAIN ----------------
while True:
    music_idx, skin_idx = start_menu()

    while True:
        final_score = game_loop(BG_MUSIC[music_idx], SKINS[skin_idx]["color"])
        restart = game_over_screen(final_score)

        if restart:
            continue      # restart game with same settings
        else:
            break         # go back to main menu
