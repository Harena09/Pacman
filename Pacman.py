import pygame
import sys
import os

pygame.init()  


WIDTH = 750
HEIGHT = 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))  
pygame.display.set_caption("Pacman")  


BLACK = (0, 0, 0)
BLUE = (0, 0, 255)



BLOCK_SIZE = 27
WALL_WIDTH = 19
WALL_HEIGHT = 31
MAZE = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.              .#     ",
    "######.## ###  ### ##.######",
    "      .## #      # ##.      ",
    "######.## #      # ##.######",
    "     #.## #      # ##.#     ",
    "     #.## #      # ##.#     ",
    "######.## ######## ##.######",
    "#......              ......#",
    "#.####.##############.####.#",
    "#.####.##############.####.#",
    "#...##................##...#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]


# Pacman images
pacman_images = [pygame.image.load(os.path.join('img', 'yellow' + str(i) + '.png')).convert_alpha()
                 for i in range(1, 5)]

# ghost images
ghost_images = {
    "pinky": pygame.image.load(os.path.join('ghost', 'pink.png')).convert_alpha(),
    "blinky": pygame.image.load(os.path.join('ghost', 'red.png')).convert_alpha(),
    "inky": pygame.image.load(os.path.join('ghost', 'orange.png')).convert_alpha(),
    "clyde": pygame.image.load(os.path.join('ghost', 'blue.png')).convert_alpha()  
}



class Pellet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((4, 4))  # Small surface for pellet
        self.image.fill(pygame.Color('white'))  # White color for pellet
        self.rect = self.image.get_rect(center=(x, y))
        self.visible = True


# create pellets and add them to the group
pellets_group = pygame.sprite.Group()
for y in range(len(MAZE)):
    for x in range(len(MAZE[y])):
        if MAZE[y][x] == ".":
            pellet = Pellet(x * BLOCK_SIZE + BLOCK_SIZE // 2, y * BLOCK_SIZE + BLOCK_SIZE // 2)
            pellets_group.add(pellet)





class Ghost(pygame.sprite.Sprite):
    def __init__(self, directions, initial_pos, ghost_type):
        pygame.sprite.Sprite.__init__(self)
        self.directions = directions
        self.current_direction_index = 0
        self.speed = 1  
        self.image = pygame.transform.scale(ghost_images[ghost_type], (BLOCK_SIZE, BLOCK_SIZE))  
        self.rect = self.image.get_rect(center=initial_pos)

    def update(self):
        if self.current_direction_index < len(self.directions):
            dx, dy, count = self.directions[self.current_direction_index]
            # new position is calculated based on speed and direction
            new_x = self.rect.x + dx * self.speed
            new_y = self.rect.y + dy * self.speed
            # Check for collision with wall (excluding blue blocks)
            if not collides_with_blue_block(new_x, new_y):
                # Move the ghost to the new position 
                if 0 <= new_x <= WIDTH - BLOCK_SIZE and 0 <= new_y <= HEIGHT - BLOCK_SIZE:
                    self.rect.x = new_x
                    self.rect.y = new_y
            count -= 1
            if count == 0:
                self.current_direction_index += 1

    def handle_collision(self):
    # Check collision with each wall
     for wall in walls_group:
        if self.rect.colliderect(wall.rect):
            # If collision occurs, stop movement in current direction
            self.current_direction_index += 1  # Move to the next direction
            break  


def collides_with_blue_block(x, y):
    # Check if the position collides with any blue blocks (walls)
    for wall in walls_group:
        if wall.image.get_at((0, 0)) == pygame.Color('blue') and wall.rect.collidepoint(x, y):
            return True
    return False




def chase_pacman(ghost, pacman):
    # Calculate direction towards Pacman
    dx = pacman.rect.centerx - ghost.rect.centerx
    dy = pacman.rect.centery - ghost.rect.centery

    # Move towards Pacman by adjusting the ghost's position
    if abs(dx) > abs(dy):
        if dx > 0:
            new_x = ghost.rect.x + ghost.speed
            if 0 <= new_x <= WIDTH - BLOCK_SIZE and not collides_with_wall(new_x, ghost.rect.y):
                ghost.rect.x = new_x
        else:
            new_x = ghost.rect.x - ghost.speed
            if 0 <= new_x <= WIDTH - BLOCK_SIZE and not collides_with_wall(new_x, ghost.rect.y):
                ghost.rect.x = new_x
    else:
        if dy > 0:
            new_y = ghost.rect.y + ghost.speed
            if 0 <= new_y <= HEIGHT - BLOCK_SIZE and not collides_with_wall(ghost.rect.x, new_y):
                ghost.rect.y = new_y
        else:
            new_y = ghost.rect.y - ghost.speed
            if 0 <= new_y <= HEIGHT - BLOCK_SIZE and not collides_with_wall(ghost.rect.x, new_y):
                ghost.rect.y = new_y



# function to check if a position collides with a wall
def collides_with_wall(x, y):
    for wall in walls_group:
        if wall.rect.collidepoint(x, y):
            return True
    return False

# Update function for ghosts
def update_ghosts(pacman):
    for ghost in ghosts_group:
        chase_pacman(ghost, pacman)
        
        # Ensure ghost's position is within the maze boundaries and handle collisions with walls
        ghost.handle_collision()

        

# Create Pacman class
class Pacman(pygame.sprite.Sprite):
    def __init__(self, initial_pos):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE)) for image in pacman_images]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=initial_pos)
        self.speed = 3  
        self.animation_speed = 0.2 
        self.last_update = pygame.time.get_ticks() 
        self.direction = None

    def update(self):
        # Update animation frame based on animation speed
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:  
            self.last_update = now
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

        # Update Pacman's movement based on direction
        if self.direction == 0:  # Right
            self.rect.x += self.speed
        elif self.direction == 1:  # Left
            self.rect.x -= self.speed
        elif self.direction == 2:  # Up
            self.rect.y -= self.speed
        elif self.direction == 3:  # Down
            self.rect.y += self.speed

        # Handle collisions with walls
        self.handle_collision()  

    def handle_collision(self):
        # Check collision with each wall
        for wall in walls_group:
            if self.rect.colliderect(wall.rect):
                # Undo movement if collision occurs
                if self.direction == 0:
                    self.rect.right = wall.rect.left
                elif self.direction == 1:
                    self.rect.left = wall.rect.right
                elif self.direction == 2:
                    self.rect.top = wall.rect.bottom
                elif self.direction == 3:
                    self.rect.bottom = wall.rect.top

#  Wall class
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x * BLOCK_SIZE, y * BLOCK_SIZE))


# sprite groups
all_sprites = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
ghosts_group = pygame.sprite.Group()  

# wall sprites and add them to the group
for y in range(len(MAZE)):
    for x in range(len(MAZE[y])):
        if MAZE[y][x] == "#":
            wall = Wall(x, y)
            walls_group.add(wall)
            all_sprites.add(wall)

# movement patterns for Pinky and Blinky
Pinky_Blinky_directions = [
    [0, -30, 4],    # Up
    [15, 0, 9],     # Right
    [0, 15, 11],    # Down
    [-15, 0, 23],   # Left
]

# movement patterns for Inky and Clyde
Inky_Clyde_directions = [
    [30, 0, 2],     # Right
    [0, -15, 4],    # Up
    [15, 0, 10],    # Right
    [0, 15, 7],     # Down
    [-15, 0, 3],    # Left
    [0, -15, 7],    # Up
    [-15, 0, 15],   # Left
    [0, 15, 3],     # Down
    [15, 0, 15],    # Right
    [0, -15, 3],    # Up
    [-15, 0, 11],   # Left
    [0, -15, 7],    # Up
    [15, 0, 3],     # Right
    [0, -15, 11],   # Up
    [15, 0, 9]      # Right
]

# direction lists to Pinky and Blinky
pinky = Ghost(Pinky_Blinky_directions, (50, 50), "pinky")
blinky = Ghost(Pinky_Blinky_directions[::-1], (WIDTH - 50, 50), "blinky")  # Reversed for symmetry

#direction lists to Inky and Clyde
inky = Ghost(Inky_Clyde_directions, (50, HEIGHT - 50), "inky")
clyde = Ghost(Inky_Clyde_directions[::-1], (WIDTH - 50, HEIGHT - 50), "clyde")  # Reversed for symmetry



ghosts_group.add(pinky, blinky, inky, clyde)
all_sprites.add(pinky, blinky, inky, clyde)

# Create Pacman sprite and add it to the group
pacman = Pacman((WIDTH // 2, HEIGHT // 2))
all_sprites.add(pacman)



# Function to draw the Pacman logo
def draw_logo():
    pacman_logo = pygame.image.load("pacmanlogo.png")
    scaled_logo = pygame.transform.scale(pacman_logo, (400, 250))
    logo_rect = scaled_logo.get_rect(center=(WIDTH // 2, 100))
    screen.blit(scaled_logo, logo_rect)



# Function to draw buttons
def draw_button(text, position):
    font = pygame.font.Font("freesansbold.ttf", 24)
    button_text = font.render(text, True, pygame.Color('white'))
    rect = button_text.get_rect(center=position)
    screen.blit(button_text, rect.topleft)
    return rect

#update high scores with the current user's score
def update_high_scores(score, name, file_path):
    high_scores = get_high_scores(file_path)
    high_scores.append((score, name))
    high_scores.sort(reverse=True)  
    high_scores = high_scores[:]  
    save_high_scores(high_scores, file_path)

# save highscores 
def save_high_scores(high_scores, file_path):
    try:
        with open(file_path, "w") as f:
            for score, name in high_scores:
                f.write(f"{score} {name}\n")
    except IOError:
        print("Error: Unable to save high scores.")

# Function to parse high scores from a list of strings
def get_high_scores(score_strings):
    try:
        high_scores = []
        for line in score_strings:
            parts = line.split()
            if len(parts) == 2:
                score = int(parts[0])
                name = " ".join(parts[1:])
                high_scores.append((score, name))
        return high_scores
    except IOError:
        print("Error: Unable to parse high scores.")
        return []

# Define a list to store high scores
high_scores = []

# Add this function to get the username from the player
def get_username(screen):
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(100, 100, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((30, 30, 30))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        
    return text  





#menu loop
def main_menu():
    show_logo = True  
    username = "" 
    while True:
        screen.fill(pygame.Color('black'))

        if show_logo:
            draw_logo() 

        # buttons 
        play_button_rect = draw_button("Play", (WIDTH // 2, HEIGHT // 2 - 50))
        username_button_rect = draw_button("Username", (WIDTH // 2, HEIGHT // 2))
        exit_button_rect = draw_button("Exit", (WIDTH // 2, HEIGHT // 2 + 50))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    # Check if any button is clicked
                    if play_button_rect.collidepoint(event.pos):
                        print("Play button clicked!")
                        # Proceed with the game
                        return username  # Exit the main_menu function after clicking play button
                    
                    elif username_button_rect.collidepoint(event.pos):
                        username = get_username(screen)  # Get the username

                    elif exit_button_rect.collidepoint(event.pos):  # Check if Exit button is clicked
                           pygame.quit()
                           sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    pacman.direction = 0  # Right
                elif event.key == pygame.K_LEFT:
                    pacman.direction = 1  # Left
                elif event.key == pygame.K_UP:
                    pacman.direction = 2  # Up
                elif event.key == pygame.K_DOWN:
                    pacman.direction = 3  # Down

                    # Function to draw only maze walls
def draw_maze_walls_only():
    screen.fill(BLACK)  # Clear the screen
    for y, row in enumerate(MAZE):
        for x, col in enumerate(row):
            if col == '#':
                pygame.draw.rect(screen, BLUE, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    pygame.display.flip()


# Call main_menu function
username = main_menu()

main_menu()



def update_pacman_position(pacman):
    if pacman.direction is not None:
        # new position is calculated based on pacman's direction
        dx, dy = 0, 0
        if pacman.direction == 0:  # Right
            dx = pacman.speed
        elif pacman.direction == 1:  # Left
            dx = -pacman.speed
        elif pacman.direction == 2:  # Up
            dy = -pacman.speed
        elif pacman.direction == 3:  # Down
            dy = pacman.speed

        new_x = pacman.rect.x + dx
        new_y = pacman.rect.y + dy

        # Check collisions with walls
        if not collides_with_wall(new_x, new_y):
            pacman.rect.x = new_x
            pacman.rect.y = new_y


def update_ghost_position(ghost):
    if ghost.current_direction_index < len(ghost.directions):
        dx, dy, count = ghost.directions[ghost.current_direction_index]
        # Calculate new position based on direction
        new_x = ghost.rect.x + dx
        new_y = ghost.rect.y + dy
        # Check for collisions with walls and blue blocks
        if not collides_with_blue_block(new_x, new_y):
            if 0 <= new_x <= WIDTH - BLOCK_SIZE and 0 <= new_y <= HEIGHT - BLOCK_SIZE:
                ghost.rect.x = new_x
                ghost.rect.y = new_y
        count -= 1
        if count == 0:
            ghost.current_direction_index += 1

pacman_lives = 3

# Main game loop
running = True
score = 0

while running and pacman_lives > 0:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        pacman.direction = 1
    elif keys[pygame.K_RIGHT]:
        pacman.direction = 0
    elif keys[pygame.K_UP]:
        pacman.direction = 2
    elif keys[pygame.K_DOWN]:
        pacman.direction = 3

    # Update sprites
    all_sprites.update()

    update_ghosts(pacman)  # Update ghosts



    if pygame.sprite.spritecollideany(pacman, pellets_group):
   
        score += 10  # Increase the score
        
        # Remove the pellet from the group
        pellet.kill()
    
    

    # Check for collisions with ghosts
    if pygame.sprite.spritecollideany(pacman, ghosts_group):
        pacman_lives -= 1
        pacman.rect.center = (WIDTH // 2, HEIGHT // 2)  # Reset Pacman's position
        for ghost in ghosts_group:
           # Assigning simplified direction lists to Pinky and Blinky
             pinky = Ghost(Pinky_Blinky_directions, (50, 50), "pinky")
             blinky = Ghost(Pinky_Blinky_directions[::-1], (WIDTH - 50, 50), "blinky")  # Reversed for symmetry

              # Assigning simplified direction lists to Inky and Clyde
             inky = Ghost(Inky_Clyde_directions, (50, HEIGHT - 50), "inky")
             clyde = Ghost(Inky_Clyde_directions[::-1], (WIDTH - 50, HEIGHT - 50), "clyde")  # Reversed for symmetry


        pygame.time.delay(1000)  # Delay to show collision effect

    # check pacman collision with pellets
    pellets_eaten = pygame.sprite.spritecollide(pacman, pellets_group, True)
    score += len(pellets_eaten)  # Increase score by the number of pellets eaten

    # Handle collisions for Pacman
    pacman.handle_collision()

    # Handle collisions for ghosts
    for ghost in ghosts_group:
        ghost.handle_collision()

    # Clear the screen
    screen.fill(pygame.Color('black'))

    # Draw all sprites
    all_sprites.draw(screen)

    # Draw pellets
    pellets_group.draw(screen)

    # Draw lives counter
    font = pygame.font.Font(None, 36)
    lives_text = font.render("Lives: " + str(pacman_lives), True, pygame.Color('white'))
    screen.blit(lives_text, (10, 10))

  # Draw lives counter
    font = pygame.font.Font(None, 36)
    score_text = font.render("Score: " + str(score), True, pygame.Color('white'))
    screen.blit(score_text, (200, 10))


    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Game over
game_over_font = pygame.font.Font(None, 73)
game_over_text = game_over_font.render("Game Over", True, pygame.Color('red'))
screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
pygame.display.flip()


# Update high scores if the current score is higher than any of the existing high scores
update_high_scores(score, username, "highscores.txt")
main_menu()
# Wait for a moment before quitting
pygame.time.delay(3000)

# Quit Pygame
pygame.quit()
sys.exit()