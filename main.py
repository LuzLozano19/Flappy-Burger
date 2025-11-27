import asyncio
import pygame
import random
import sys

pygame.init()
clock = pygame.time.Clock()

# --- WINDOW ---
WIDTH, HEIGHT = 400, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Burger - Pixel Art Sunset")

# --- COLORS ---
PURPLE = (40, 0, 60)
PINK = (255, 100, 180)
ORANGE = (255, 140, 60)

# --- ASSETS ---
IMG_HAMBURGER = "bienvenidos.png"
IMG_PIPES = "papas.png"
IMG_LOGO = "logo.png"

SND_HIT = "hit.wav"
SND_SCORE = "score.wav"
MUSIC = "music.mp3"

# --- GAME CONFIG ---
HAMB_SIZE = 90
PIPE_W, PIPE_H = 120, 300
PIPE_GAP = 180
PIPE_SPEED = 3
GRAVITY = 0.5
PLAYER_X = 80

font = pygame.font.SysFont("pixel", 36, bold=True)
small_font = pygame.font.SysFont("pixel", 24, bold=True)


# ------- SAFE LOADERS -------
def safe_image_load(path, fallback_size=(50, 50)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return img
    except Exception:
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        surf.fill((255, 0, 255, 200))
        return surf


def safe_sound_load(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None


# imágenes
hamburguer_img = safe_image_load(IMG_HAMBURGER, (HAMB_SIZE, HAMB_SIZE))
hamburguer_img = pygame.transform.scale(hamburguer_img, (HAMB_SIZE, HAMB_SIZE))

pipe_img = safe_image_load(IMG_PIPES, (PIPE_W, PIPE_H))
pipe_img = pygame.transform.scale(pipe_img, (PIPE_W, PIPE_H))
pipe_img_flipped = pygame.transform.flip(pipe_img, False, True)

logo_img = safe_image_load(IMG_LOGO, (80, 100))
logo_img = pygame.transform.scale(logo_img, (80, 100))

# sonidos
hit_sound = safe_sound_load(SND_HIT)
score_sound = safe_sound_load(SND_SCORE)

try:
    pygame.mixer.music.load(MUSIC)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
except Exception:
    pass


# ------- DRAW HELPERS -------
def draw_pixel_gradient(surface):
    pixel_size = 4
    for y in range(0, HEIGHT, pixel_size):
        t = y / HEIGHT
        if t < 0.33:
            ratio = t / 0.33
            r = PURPLE[0] + (PINK[0] - PURPLE[0]) * ratio
            g = PURPLE[1] + (PINK[1] - PURPLE[1]) * ratio
            b = PURPLE[2] + (PINK[2] - PURPLE[2]) * ratio
        elif t < 0.66:
            ratio = (t - 0.33) / 0.33
            r = PINK[0] + (ORANGE[0] - PINK[0]) * ratio
            g = PINK[1] + (ORANGE[1] - PINK[1]) * ratio
            b = PINK[2] + (ORANGE[2] - PINK[2]) * ratio
        else:
            r, g, b = ORANGE

        pygame.draw.rect(surface, (int(r), int(g), int(b)), (0, y, WIDTH, pixel_size))


def draw_text_shadow(surface, text, fontobj, color, x, y):
    shadow = fontobj.render(text, True, (0, 0, 0))
    surface.blit(shadow, (x + 3, y + 3))
    label = fontobj.render(text, True, color)
    surface.blit(label, (x, y))


# ------- TOUCH DETECTION -------
def is_touch_event(event):
    """Detecta tap en celular (pygbag traduce el touch a MOUSEBUTTONDOWN)."""
    return event.type == pygame.MOUSEBUTTONDOWN


# ------- SCREENS -------
async def game_over_screen(score):
    if hit_sound:
        try:
            hit_sound.play()
        except:
            pass

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            # SPACE o TOUCH = retry
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or is_touch_event(event):
                return "retry"

        draw_pixel_gradient(WINDOW)

        text = font.render("GAME OVER", True, (255, 255, 255))
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        retry_text = small_font.render("Toca la pantalla para jugar de nuevo", True, (255, 255, 255))

        WINDOW.blit(text, (WIDTH // 2 - text.get_width() // 2, 200))
        WINDOW.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 260))
        WINDOW.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, 330))

        pygame.display.update()
        clock.tick(60)
        await asyncio.sleep(0)


async def start_screen():
    float_offset = 0
    float_direction = 1
    blink_timer = 0

    TITLE_COLOR = (150, 60, 255)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            # SPACE o TOUCH = start
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or is_touch_event(event):
                return "start"

        draw_pixel_gradient(WINDOW)

        float_offset += float_direction * 0.4
        if float_offset > 10:
            float_direction = -1
        if float_offset < -10:
            float_direction = 1

        WINDOW.blit(hamburguer_img, (WIDTH // 2 - HAMB_SIZE // 2, 140 + float_offset))

        title_text = "FLAPPY BURGER"
        title_surface = font.render(title_text, True, TITLE_COLOR)
        draw_text_shadow(WINDOW, title_text, font, TITLE_COLOR,
                         WIDTH // 2 - title_surface.get_width() // 2, 40)

        promo1 = small_font.render("Consigue un score de 50", True, (255, 255, 255))
        promo2 = small_font.render("para unas papas gratis!!", True, (255, 255, 255))
        WINDOW.blit(promo1, (WIDTH // 2 - promo1.get_width() // 2, 300))
        WINDOW.blit(promo2, (WIDTH // 2 - promo2.get_width() // 2, 325))

        blink_timer += 1
        if (blink_timer // 30) % 2 == 0:
            start_text = small_font.render("Toca la pantalla para comenzar", True, (255, 255, 255))
            WINDOW.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 420))

        WINDOW.blit(logo_img, (10, 10))

        pygame.display.update()
        clock.tick(60)
        await asyncio.sleep(0)


async def game_loop():
    player_y = HEIGHT // 2
    player_vel = 0
    pipes = []
    spawn_timer = 0
    score = 0

    while True:

        # input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            # SALTO: teclado o pantalla
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or is_touch_event(event):
                player_vel = -7

        # Física
        player_vel += GRAVITY
        player_y += player_vel

        # Spawn pipes
        spawn_timer += 1
        if spawn_timer > 100:
            spawn_timer = 0
            top_height = random.randint(80, HEIGHT - PIPE_GAP - 80)
            pipes.append([WIDTH, top_height])

        for pipe in pipes:
            pipe[0] -= PIPE_SPEED

        pipes = [p for p in pipes if p[0] + PIPE_W > 0]

        # Score
        for pipe_x, _ in pipes:
            if pipe_x + PIPE_W < PLAYER_X <= pipe_x + PIPE_W + PIPE_SPEED:
                score += 1
                if score_sound:
                    try:
                        score_sound.play()
                    except:
                        pass

        # Collision
        HITBOX_REDUCTION = 20
        player_rect = pygame.Rect(
            PLAYER_X + HITBOX_REDUCTION,
            player_y + HITBOX_REDUCTION,
            HAMB_SIZE - HITBOX_REDUCTION * 2,
            HAMB_SIZE - HITBOX_REDUCTION * 2
        )

        collided = False
        for pipe_x, top_h in pipes:
            top_rect = pygame.Rect(pipe_x, top_h - PIPE_H, PIPE_W, PIPE_H)
            bottom_rect = pygame.Rect(pipe_x, top_h + PIPE_GAP, PIPE_W, PIPE_H)

            if player_rect.colliderect(top_rect) or player_rect.colliderect(bottom_rect):
                collided = True
                break

        if player_y <= -10 or player_y + HAMB_SIZE >= HEIGHT + 10:
            collided = True

        # Draw
        draw_pixel_gradient(WINDOW)

        for pipe_x, top_h in pipes:
            WINDOW.blit(pipe_img_flipped, (pipe_x, top_h - PIPE_H))
            WINDOW.blit(pipe_img, (pipe_x, top_h + PIPE_GAP))

        WINDOW.blit(hamburguer_img, (PLAYER_X, int(player_y)))

        score_text = font.render(str(score), True, (255, 255, 255))
        WINDOW.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
        WINDOW.blit(logo_img, (10, 10))

        pygame.display.update()
        clock.tick(60)

        await asyncio.sleep(0)

        if collided:
            return score


# ------- MAIN -------
async def main():
    while True:
        r = await start_screen()
        if r == "quit":
            return

        score = await game_loop()
        if score == "quit":
            return

        r2 = await game_over_screen(score)
        if r2 == "quit":
            return


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        pygame.quit()
