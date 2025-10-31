import pygame, random, sys

pygame.init()

# --- Screen setup ---
WIDTH, HEIGHT = 800, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump to Dodge - Save Melony Mission")

clock = pygame.time.Clock()
FPS = 60

# --- Load Images ---
bg_img = pygame.image.load("background.png").convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

player_img = pygame.image.load("player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (60, 60))

# --- Load obstacle images & sounds ---
obstacle_data = [
    {"img": pygame.image.load("obstacle1.png").convert_alpha(), "sound": "death1.wav"},
    {"img": pygame.image.load("obstacle2.png").convert_alpha(), "sound": "death2.wav"},
    {"img": pygame.image.load("obstacle3.png").convert_alpha(), "sound": "death3.wav"},
    {"img": pygame.image.load("obstacle4_big.png").convert_alpha(), "sound": "death4.wav"},  # big only wave 4
    {"img": pygame.image.load("obstacle5.png").convert_alpha(), "sound": "death5.wav"},
]
for o in obstacle_data:
    o["img"] = pygame.transform.scale(o["img"], (80, 80) if "big" in o["sound"] else (60, 60))
    o["sound"] = pygame.mixer.Sound(o["sound"])

# --- Sounds ---
win_sound = pygame.mixer.Sound("win.wav")
pygame.mixer.music.load("main_theme.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# --- Variables ---
player_x = 100
player_y = HEIGHT - 60 - 50
player_vel_y = 0
gravity = 1
is_jumping = False
can_double_jump = False
double_jump_used = False
last_tap_time = 0

# Obstacles
obstacle_x = WIDTH
obstacle_y = HEIGHT - 60 - 50
obstacle_vel = 8
obstacle_type = 0

# Waves
rizz_level = 0
wave = 1
max_wave = 5
rizz_to_next_wave = 5

# Fonts
font = pygame.font.SysFont("arial", 30)
big_font = pygame.font.SysFont("arial", 48)

# Game states
game_over = False
game_won = False
in_lobby = True
show_double_jump_msg = False

def reset_game():
    global player_y, player_vel_y, is_jumping, double_jump_used, can_double_jump
    global obstacle_x, obstacle_vel, rizz_level, wave, game_over, game_won
    global in_lobby, obstacle_type, show_double_jump_msg

    player_y = HEIGHT - 60 - 50
    player_vel_y = 0
    is_jumping = False
    double_jump_used = False
    can_double_jump = False
    obstacle_x = WIDTH
    obstacle_vel = 8
    rizz_level = 0
    wave = 1
    game_over = False
    game_won = False
    in_lobby = True
    obstacle_type = 0
    show_double_jump_msg = False


def handle_jump():
    """Handle single and double jump logic."""
    global is_jumping, player_vel_y, double_jump_used, can_double_jump, last_tap_time
    current_time = pygame.time.get_ticks()
    time_diff = current_time - last_tap_time
    last_tap_time = current_time

    if not is_jumping:
        is_jumping = True
        player_vel_y = -18
        double_jump_used = False
    elif can_double_jump and not double_jump_used and time_diff < 300:
        player_vel_y = -20
        double_jump_used = True


def main():
    global player_y, player_vel_y, is_jumping, obstacle_x, obstacle_vel
    global rizz_level, wave, game_over, game_won, obstacle_type, in_lobby
    global show_double_jump_msg, can_double_jump

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if in_lobby:
                    in_lobby = False
                elif game_over or game_won:
                    reset_game()
                elif show_double_jump_msg:
                    show_double_jump_msg = False
                    can_double_jump = True
                    obstacle_vel = 10  # resume normal movement
                    obstacle_x = WIDTH
                else:
                    handle_jump()

        # --- Game logic ---
        if not game_over and not game_won and not in_lobby and not show_double_jump_msg:
            # Gravity
            if is_jumping:
                player_y += player_vel_y
                player_vel_y += gravity
                if player_y >= HEIGHT - 60 - 50:
                    player_y = HEIGHT - 60 - 50
                    is_jumping = False
                    double_jump_used = False

            # Move obstacle
            obstacle_x -= obstacle_vel
            if obstacle_x < -80:
                obstacle_x = WIDTH + random.randint(300, 800)
                rizz_level += 1

                # Wave progression
                if rizz_level % rizz_to_next_wave == 0:
                    wave += 1
                    if wave == 4:
                        show_double_jump_msg = True
                        obstacle_vel = 0
                        obstacle_x = WIDTH
                        obstacle_type = 3  # big obstacle
                    elif wave == 5:
                        obstacle_vel = 16  # very fast
                        obstacle_type = 4  # normal small
                    elif wave <= 3:
                        obstacle_type = wave - 1
                        obstacle_vel += 2

                    if wave > max_wave:
                        game_won = True
                        win_sound.play()

            # Collision
            size = 80 if wave == 4 else 60
            player_rect = pygame.Rect(player_x, player_y, 60, 60)
            obstacle_rect = pygame.Rect(obstacle_x, obstacle_y, size, size)
            if player_rect.colliderect(obstacle_rect):
                obstacle_data[obstacle_type]["sound"].play()
                game_over = True

        # --- Draw ---
        WIN.blit(bg_img, (0, 0))
        WIN.blit(player_img, (player_x, player_y))
        if not in_lobby and not show_double_jump_msg:
            WIN.blit(obstacle_data[obstacle_type]["img"], (obstacle_x, obstacle_y))

        # HUD
        if not in_lobby:
            rizz_text = font.render(f"Rizz Level: {rizz_level}", True, (0, 0, 0))
            wave_text = font.render(f"Wave: {wave}/{max_wave}", True, (0, 0, 0))
            WIN.blit(rizz_text, (10, 10))
            WIN.blit(wave_text, (10, 40))

        # Lobby
        if in_lobby:
            lobby_text = big_font.render("Touch to Become Powerfull Nigga", True, (0, 0, 255))
            mission_text = font.render("Mission is to save Melony!", True, (255, 0, 0))
            WIN.blit(lobby_text, (WIDTH // 2 - 150, HEIGHT // 2 - 60))
            WIN.blit(mission_text, (WIDTH // 2 - 180, HEIGHT // 2))

        # Double jump activation screen
        if show_double_jump_msg:
            msg_text = big_font.render("Double Jump Activated!", True, (0, 0, 255))
            resume_text = font.render("Tap to Use superpower", True, (0, 0, 0))
            WIN.blit(msg_text, (WIDTH // 2 - 230, HEIGHT // 2 - 60))
            WIN.blit(resume_text, (WIDTH // 2 - 90, HEIGHT // 2))

        # Game over / win
        if game_over:
            over_text = big_font.render("YOU LOST MY NIGGA", True, (255, 0, 0))
            WIN.blit(over_text, (WIDTH // 2 - 260, HEIGHT // 2 - 40))
        if game_won:
            win_text = big_font.render("YOU WON BUT AJAY IS GAY", True, (0, 150, 0))
            WIN.blit(win_text, (WIDTH // 2 - 260, HEIGHT // 2 - 40))

        pygame.display.update()


if __name__ == "__main__":
    main()
