import pygame
import random
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (34, 139, 34)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_YELLOW = (204, 204, 0)

# Game settings
LEVELS = {
    1: {"fps": 4, "apples_needed": 5},
    2: {"fps": 6, "apples_needed": 10},
    3: {"fps": 8, "apples_needed": 15},
    4: {"fps": 10, "apples_needed": float('inf')}  # Final level
}
LIVES = 3

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # Start moving right
        self.growing = False
    
    def move(self):
        head_x, head_y = self.positions[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        
        self.positions.insert(0, new_head)
        if not self.growing:
            self.positions.pop()
        else:
            self.growing = False
    
    def change_direction(self, direction):
        # Prevent moving backwards into itself
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
    
    def grow(self):
        self.growing = True
    
    def check_collision_with_border(self):
        head_x, head_y = self.positions[0]
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True
        return False
    
    def check_self_collision(self):
        return self.positions[0] in self.positions[1:]
    
    def draw(self, surface):
        # Draw body
        for i, pos in enumerate(self.positions):
            x = pos[0] * GRID_SIZE
            y = pos[1] * GRID_SIZE
            pygame.draw.rect(surface, YELLOW, (x, y, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, DARK_YELLOW, (x, y, GRID_SIZE, GRID_SIZE), 2)
            
            # Draw face on head
            if i == 0:
                # Eyes
                eye_size = 3
                pygame.draw.circle(surface, BLACK, (x + 6, y + 6), eye_size)
                pygame.draw.circle(surface, BLACK, (x + 14, y + 6), eye_size)
                # Smile
                pygame.draw.arc(surface, BLACK, (x + 4, y + 8, 12, 8), 3.14, 0, 2)

class Apple:
    def __init__(self, snake_positions):
        self.position = self.random_position(snake_positions)
    
    def random_position(self, snake_positions):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_positions:
                return pos
    
    def draw(self, surface):
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE
        pygame.draw.circle(surface, RED, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), GRID_SIZE // 2 - 2)
        # Stem
        pygame.draw.rect(surface, (139, 69, 19), (x + GRID_SIZE // 2 - 1, y, 2, 4))

def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def create_eating_sound():
    """Generate a simple eating sound effect"""
    try:
        import numpy as np
        sample_rate = 22050
        duration = 0.1  # 100ms
        frequency = 800  # Hz
        
        # Generate sound wave
        t = np.linspace(0, duration, int(sample_rate * duration))
        wave = np.sin(2 * np.pi * frequency * t)
        wave = (wave * 4096).astype(np.int16)
        
        # Create stereo sound
        stereo_wave = np.column_stack((wave, wave))
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound
    except:
        # Return None if numpy is not available
        return None

def create_happy_sound():
    """Generate a happy level-up sound effect"""
    try:
        import numpy as np
        sample_rate = 22050
        duration = 0.3  # 300ms
        
        # Create ascending notes (C, E, G)
        frequencies = [523, 659, 784]
        wave = np.array([])
        
        for freq in frequencies:
            t = np.linspace(0, duration / 3, int(sample_rate * duration / 3))
            note = np.sin(2 * np.pi * freq * t)
            wave = np.concatenate([wave, note])
        
        wave = (wave * 4096).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound
    except:
        return None

def create_sad_sound():
    """Generate a sad death sound effect"""
    try:
        import numpy as np
        sample_rate = 22050
        duration = 0.4  # 400ms
        
        # Create descending notes (G, E, C)
        frequencies = [784, 659, 523, 392]
        wave = np.array([])
        
        for freq in frequencies:
            t = np.linspace(0, duration / 4, int(sample_rate * duration / 4))
            note = np.sin(2 * np.pi * freq * t) * np.exp(-3 * t)  # Decay
            wave = np.concatenate([wave, note])
        
        wave = (wave * 4096).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound
    except:
        return None

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Hungry Snakes")
    clock = pygame.time.Clock()
    
    # Create sound effects
    eating_sound = create_eating_sound()
    happy_sound = create_happy_sound()
    sad_sound = create_sad_sound()
    
    # Game variables
    snake = Snake()
    apple = Apple(snake.positions)
    score = 0
    lives = LIVES
    level = 1
    apples_in_level = 0
    game_over = False
    level_complete = False
    
    # Main game loop
    running = True
    while running:
        clock.tick(LEVELS[level]["fps"])
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and level_complete:
                # Continue from level complete screen
                level_complete = False
            elif event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction((1, 0))
            elif event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_SPACE:
                    # Restart game
                    snake = Snake()
                    apple = Apple(snake.positions)
                    score = 0
                    lives = LIVES
                    level = 1
                    apples_in_level = 0
                    game_over = False
        
        if not game_over and not level_complete:
            # Move snake
            snake.move()
            
            # Check if snake ate apple
            if snake.positions[0] == apple.position:
                snake.grow()
                score += 1
                apples_in_level += 1
                apple = Apple(snake.positions)
                if eating_sound:
                    eating_sound.play()
                
                # Check for level up
                if apples_in_level >= LEVELS[level]["apples_needed"] and level < 4:
                    level += 1
                    apples_in_level = 0
                    level_complete = True
                    if happy_sound:
                        happy_sound.play()
            
            # Check collisions
            if snake.check_collision_with_border():
                lives -= 1
                if sad_sound:
                    sad_sound.play()
                if lives <= 0:
                    game_over = True
                else:
                    # Reset snake position
                    snake = Snake()
                    apple = Apple(snake.positions)
            
            # Check self collision
            if snake.check_self_collision():
                lives -= 1
                if sad_sound:
                    sad_sound.play()
                if lives <= 0:
                    game_over = True
                else:
                    snake = Snake()
                    apple = Apple(snake.positions)
        
        # Drawing
        screen.fill(GREEN)
        
        # Draw border
        pygame.draw.rect(screen, BLACK, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 3)
        
        if level_complete:
            # Draw level complete celebration screen
            snake.draw(screen)
            apple.draw(screen)
            
            # Semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((50, 50, 100))
            screen.blit(overlay, (0, 0))
            
            # Draw celebration elements
            # Stars/sparkles
            star_positions = [(100, 100), (500, 100), (100, 500), (500, 500), 
                            (300, 80), (300, 520), (50, 300), (550, 300)]
            for star_pos in star_positions:
                pygame.draw.circle(screen, (255, 255, 0), star_pos, 8)
                pygame.draw.circle(screen, WHITE, star_pos, 4)
            
            # Celebration text
            draw_text(screen, "🎉 YAY! 🎉", 72, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 120, (255, 215, 0))
            draw_text(screen, f"You Completed Level {level - 1}!", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40, WHITE)
            draw_text(screen, f"Now entering Level {level}", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20, (173, 216, 230))
            draw_text(screen, "Press any key to continue", 28, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80, (144, 238, 144))
            
            # Draw border around text
            pygame.draw.rect(screen, (255, 215, 0), (80, WINDOW_HEIGHT // 2 - 160, WINDOW_WIDTH - 160, 280), 4)
            
        elif not game_over:
            snake.draw(screen)
            apple.draw(screen)
        else:
            draw_text(screen, "GAME OVER!", 64, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50, RED)
            draw_text(screen, f"Final Score: {score}", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20, WHITE)
            draw_text(screen, "Press SPACE to play again", 24, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70, WHITE)
        
        # Draw score and lives
        draw_text(screen, f"Score: {score}", 30, 60, 10, WHITE)
        draw_text(screen, f"Level: {level}", 30, WINDOW_WIDTH // 2, 10, WHITE)
        draw_text(screen, f"Lives: {'❤ ' * lives}", 30, WINDOW_WIDTH - 80, 10, RED)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
