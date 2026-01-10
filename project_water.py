import pygame
from random import randint, choice, random
import math

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

WIN_WIDTH = 1280
WIN_HEIGHT = 720
window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Waterstorm")

songs = ["Wait.mp3", "Viscera.mp3", "BTH.mp3"]
SONG_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(SONG_END)

current_song = choice(songs)
pygame.mixer.music.load(current_song)
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.0)

bg = pygame.transform.scale(
    pygame.transform.flip(pygame.image.load("ocean.webp"), True, False),
    (WIN_WIDTH, WIN_HEIGHT)
)

player_img = pygame.transform.scale(pygame.image.load("car.png"), (60, 60))
ai_img = pygame.transform.scale(pygame.image.load("car2.png"), (60, 60))
trash_img = pygame.transform.scale(pygame.image.load("banana peel.jpeg"), (40, 40))
fish_img = pygame.transform.scale(pygame.image.load("fish.png"), (40, 40))

font = pygame.font.SysFont(None, 60)
small_font = pygame.font.SysFont(None, 36)

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 50, 50)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)

game_state = "difficulty"
difficulty = "Normal"

DIFFICULTY_DATA = {
    "Easy":   {"speed": 4,   "mistake": 0.04},
    "Normal": {"speed": 5,   "mistake": 0.02},
    "Hard":   {"speed": 6.5, "mistake": 0.005},
}

BORDER_SIZE = 20
borders = [
    pygame.Rect(0, 0, WIN_WIDTH, BORDER_SIZE),
    pygame.Rect(0, WIN_HEIGHT - BORDER_SIZE, WIN_WIDTH, BORDER_SIZE),
    pygame.Rect(0, 0, BORDER_SIZE, WIN_HEIGHT),
    pygame.Rect(WIN_WIDTH - BORDER_SIZE, 0, BORDER_SIZE, WIN_HEIGHT),
]

trash_list = [
    pygame.Rect(randint(100, WIN_WIDTH - 100), randint(100, WIN_HEIGHT - 100), 40, 40)
    for _ in range(6)
]

def find_nearest_trash(pos):
    return min(trash_list, key=lambda t: pos.distance_to(t.center))

def respawn_trash(t):
    t.x = randint(100, WIN_WIDTH - 100)
    t.y = randint(100, WIN_HEIGHT - 100)

def avoid_puddles(pos, desired, difficulty):
    if difficulty == "Easy":
        return desired

    avoid_strength = 1.5 if difficulty == "Normal" else 3.0
    avoid_radius = 120 if difficulty == "Normal" else 180

    for rect, _ in puddles:
        center = pygame.math.Vector2(rect.center)
        dist = pos.distance_to(center)
        if dist < avoid_radius:
            away = pos - center
            if away.length() > 0:
                away.scale_to_length(avoid_strength * (avoid_radius - dist) / avoid_radius)
                desired += away

    return desired

player_pos = pygame.math.Vector2(WIN_WIDTH // 2, WIN_HEIGHT // 2)
player_vel = pygame.math.Vector2()
player_angle = 0

ai_pos = pygame.math.Vector2(randint(200, 1000), randint(200, 500))
ai_vel = pygame.math.Vector2()
ai_angle = 0

score = 0
ai_score = 0

FISH_DROP_TIME = 15000
PUDDLE_LIFETIME = 10000

fish_pos = pygame.math.Vector2(randint(100, WIN_WIDTH-100), randint(100, WIN_HEIGHT-100))
fish_dir = pygame.math.Vector2(1, 0).rotate(randint(0, 360))
fish_speed = 2

last_puddle_time = pygame.time.get_ticks()
puddles = []

running = True
while running:
    clock.tick(60)
    window.blit(bg, (0, 0))
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == SONG_END:
            next_song = choice([s for s in songs if s != current_song])
            current_song = next_song
            pygame.mixer.music.load(current_song)
            pygame.mixer.music.play()

        if game_state == "difficulty" and event.type == pygame.MOUSEBUTTONDOWN:
            y = event.pos[1]
            if 260 < y < 300:
                difficulty = "Easy"
            elif 330 < y < 370:
                difficulty = "Normal"
            elif 400 < y < 440:
                difficulty = "Hard"
            game_state = "game"

    if game_state == "difficulty":
        title = font.render("SELECT DIFFICULTY", True, WHITE)
        window.blit(title, title.get_rect(center=(WIN_WIDTH // 2, 180)))

        for i, d in enumerate(["Easy", "Normal", "Hard"]):
            color = GREEN if d == difficulty else WHITE
            txt = font.render(d, True, color)
            window.blit(txt, txt.get_rect(center=(WIN_WIDTH // 2, 280 + i * 70)))

    if game_state == "game":
        keys = pygame.key.get_pressed()
        forward = pygame.math.Vector2(0, -1).rotate(-player_angle)

        if keys[pygame.K_UP]:
            player_vel += forward * 0.3
        if keys[pygame.K_DOWN]:
            player_vel -= forward * 0.2
        if keys[pygame.K_LEFT]:
            player_angle += 4
        if keys[pygame.K_RIGHT]:
            player_angle -= 4

        player_vel *= 0.96
        player_pos += player_vel

        ai_speed = DIFFICULTY_DATA[difficulty]["speed"]
        mistake_chance = DIFFICULTY_DATA[difficulty]["mistake"]

        target = find_nearest_trash(ai_pos)
        desired = pygame.math.Vector2(target.center) - ai_pos

        desired = avoid_puddles(ai_pos, desired, difficulty)

        if random() < mistake_chance:
            desired.rotate_ip(randint(-90, 90))

        desired_angle = desired.angle_to(pygame.math.Vector2(0, -1))
        diff = (desired_angle - ai_angle + 180) % 360 - 180
        ai_angle += max(-3, min(3, diff))

        ai_forward = pygame.math.Vector2(0, -1).rotate(-ai_angle)
        ai_vel += ai_forward * 0.2

        if ai_vel.length() > ai_speed:
            ai_vel.scale_to_length(ai_speed)

        ai_vel *= 0.97
        ai_pos += ai_vel

        fish_pos += fish_dir * fish_speed
        if fish_pos.x < 40 or fish_pos.x > WIN_WIDTH - 40:
            fish_dir.x *= -1
        if fish_pos.y < 40 or fish_pos.y > WIN_HEIGHT - 40:
            fish_dir.y *= -1
        if random() < 0.02:
            fish_dir.rotate_ip(randint(-30, 30))

        if now - last_puddle_time >= FISH_DROP_TIME:
            puddles.append((pygame.Rect(fish_pos.x-30, fish_pos.y-30, 60, 60), now))
            last_puddle_time = now

        p_img = pygame.transform.rotate(player_img, player_angle)
        a_img = pygame.transform.rotate(ai_img, ai_angle)
        p_rect = p_img.get_rect(center=player_pos)
        a_rect = a_img.get_rect(center=ai_pos)


        for rect, spawn in puddles[:]:
            if now - spawn > PUDDLE_LIFETIME:
                puddles.remove((rect, spawn))
            else:
                pygame.draw.ellipse(window, (30, 100, 200), rect)

                if p_rect.colliderect(rect):
                    spin = min(40, player_vel.length() * 6)
                    player_vel.rotate_ip(randint(-int(spin), int(spin)))
                    player_vel *= 1.03

                if a_rect.colliderect(rect):
                    spin = min(35, ai_vel.length() * 5)
                    ai_vel.rotate_ip(randint(-int(spin), int(spin)))
                    ai_vel *= 1.02

        for border in borders:
            if p_rect.colliderect(border):
                player_vel *= -0.7
            if a_rect.colliderect(border):
                ai_vel *= -0.7

        if p_rect.colliderect(a_rect):
            player_vel *= -0.6
            ai_vel *= -0.6

        for t in trash_list:
            window.blit(trash_img, t)
            if p_rect.colliderect(t):
                score += 1
                respawn_trash(t)
            if a_rect.colliderect(t):
                ai_score += 1
                respawn_trash(t)

        window.blit(p_img, p_rect)
        window.blit(a_img, a_rect)

        window.blit(fish_img, fish_img.get_rect(center=fish_pos))

        for border in borders:
            pygame.draw.rect(window, GRAY, border)

        window.blit(font.render(f"You: {score}", True, WHITE), (20, 20))
        window.blit(font.render(f"AI: {ai_score}", True, RED), (20, 80))
        window.blit(small_font.render(f"Difficulty: {difficulty}", True, WHITE), (20, 140))

    pygame.display.update()

pygame.quit()