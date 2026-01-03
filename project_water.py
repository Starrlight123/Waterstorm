import pygame
from random import randint, choice

pygame.init()
clock = pygame.time.Clock()

pygame.init()
pygame.mixer.init()

songs = ["Cottonmouth.mp3", "Master of disguise.mp3"]

current_song = choice(songs)
pygame.mixer.music.load(current_song)
pygame.mixer.music.play(-1)

img_background = pygame.image.load("road.jpg")
icon = pygame.image.load("Game_Icon.png")
car_img = pygame.image.load("car.png")
trash1_img = pygame.image.load("banana peel.jpeg")

car_img = pygame.transform.scale(car_img, (60, 60))
trash1_img = pygame.transform.scale(trash1_img, (40, 40))
img_background = pygame.transform.flip(img_background, True, False) 

pygame.display.set_icon(icon)

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)

font = pygame.font.SysFont(None, 60)
small_font = pygame.font.SysFont(None, 36)

win_width = 1280
win_height = 720
pygame.display.set_caption("Waterstorm")
window = pygame.display.set_mode((win_width, win_height))
img_background = pygame.transform.scale(img_background, (win_width, win_height))

game_state = "instructions"
button_rect = pygame.Rect(win_width//2 - 100, win_height//2 - 50, 200, 100)
trash_list = [pygame.Rect(randint(50, win_width - 50), randint(50, win_height - 50), 40, 40) for _ in range(5)]
score = 0

car_x = win_width // 2
car_y = win_height // 2
velocity_x = 0
velocity_y = 0
acceleration = 0.25
friction = 0.03
max_speed = 6
turn_speed = 3
angle = 0

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "instructions":
                game_state = "menu"
            elif game_state == "menu":
                if button_rect.collidepoint(event.pos):
                    game_state = "game"
                how_rect = pygame.Rect(win_width//2 - 150, win_height//2 + 100, 300, 50)
                if how_rect.collidepoint(event.pos):
                    game_state = "instructions"

    window.blit(img_background, (0, 0))

    if game_state == "instructions":
        title = font.render("HOW TO PLAY", True, WHITE)
        window.blit(title, title.get_rect(center=(win_width // 2, 120)))

        instructions = [
            "UP ARROW    - Accelerate",
            "DOWN ARROW  - Brake / Reverse",
            "LEFT ARROW  - Turn Left",
            "RIGHT ARROW - Turn Right",
            "",
            "Drive around and collect all the trash.",
            "Avoid hitting the edges too hard.",
            "",
            "Click anywhere to continue"
        ]

        for i, line in enumerate(instructions):
            text = small_font.render(line, True, WHITE)
            window.blit(text, text.get_rect(center=(win_width // 2, 220 + i * 40)))

    elif game_state == "menu":
        pygame.draw.rect(window, GREEN, button_rect)
        play_text = font.render("PLAY", True, WHITE)
        window.blit(play_text, play_text.get_rect(center=button_rect.center))

        how_text = font.render("How to Play", True, WHITE)
        how_rect = how_text.get_rect(center=(win_width // 2, win_height // 2 + 120))
        pygame.draw.rect(window, BLACK, how_rect.inflate(20, 20))
        window.blit(how_text, how_rect)

    elif game_state == "game":
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, -1).rotate(-angle)
        speed = (velocity_x**2 + velocity_y**2) ** 0.5
        effective_turn = turn_speed * (speed / max_speed)

        if keys[pygame.K_LEFT]:
            angle += effective_turn
        if keys[pygame.K_RIGHT]:
            angle -= effective_turn

        accel_strength = acceleration * (1 - (speed / max_speed))
        if keys[pygame.K_UP]:
            velocity_x += direction.x * accel_strength
            velocity_y += direction.y * accel_strength
        if keys[pygame.K_DOWN]:
            velocity_x -= direction.x * accel_strength * 0.5
            velocity_y -= direction.y * accel_strength * 0.5

        speed = (velocity_x**2 + velocity_y**2) ** 0.5
        if speed > max_speed:
            scale = max_speed / speed
            velocity_x *= scale
            velocity_y *= scale

        if not (keys[pygame.K_UP] or keys[pygame.K_DOWN]) and speed > 0.1:
            velocity_x -= friction * (velocity_x / speed)
            velocity_y -= friction * (velocity_y / speed)

        car_x += velocity_x
        car_y += velocity_y

        rotated_car = pygame.transform.rotate(car_img, angle)
        rect = rotated_car.get_rect(center=(car_x, car_y))

        if rect.left < 0:
            car_x = rect.width // 2
            velocity_x *= -0.3
        if rect.right > win_width:
            car_x = win_width - rect.width // 2
            velocity_x *= -0.3
        if rect.top < 0:
            car_y = rect.height // 2
            velocity_y *= -0.3
        if rect.bottom > win_height:
            car_y = win_height - rect.height // 2
            velocity_y *= -0.3

        for trash in trash_list:
            window.blit(trash1_img, (trash.x, trash.y))
        for trash in trash_list[:]:
            if rect.colliderect(trash):
                trash_list.remove(trash)
                score += 1

        window.blit(rotated_car, rect)

    score_text = font.render(f"Score: {score}", True, WHITE)
    window.blit(score_text, (20, 20))

    pygame.display.update()
    clock.tick(60)

pygame.quit()