import pygame
from sys import exit
from random import randint, choice

# SPRITES
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Images
        player_face_left = pygame.image.load(
            'graphics/player/player_face_left.png').convert_alpha()
        player_face_right = pygame.image.load(
            'graphics/player/player_face_right.png').convert_alpha()
        self.player_face = [player_face_left, player_face_right]
        self.image = self.player_face[1]
        self.rect = self.image.get_rect(midbottom = (640, 720))

        # Movement variables (default 10 and 20)
        self.walk_speed = 10
        self.sprint_speed = 20
    
    # Get pressed keys and move the player accordingly
    def player_input(self):
        keys = pygame.key.get_pressed()

        # Move left
        if (keys[pygame.K_LEFT] or keys[pygame.K_a])\
            and self.rect.left >= 0:

            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:  # Sprint
                self.rect.x -= self.sprint_speed
            else:  # Walk
                self.rect.x -= self.walk_speed
        
        # Move right
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d])\
            and self.rect.right <= 1280:

            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.rect.x += self.sprint_speed
            else:
                self.rect.x += self.walk_speed
    
    # When level increases, the fruits fall faster. So, player will
    # also increase their speed for difficulty adjustment.
    def set_speed(self, new_speed):
        self.walk_speed = new_speed
        self.sprint_speed = new_speed * 2
    
    # Change player's image to face left/right based on key pressed
    def animation_state(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.image = self.player_face[0]
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.image = self.player_face[1]
    
    # Called by game loop (movement + animation)
    def update(self):
        self.player_input()
        self.animation_state()

class Fruit(pygame.sprite.Sprite):
    def __init__(self, type, fall_speed):
        super().__init__()

        # Images
        if type == 'apple':
            self.image = pygame.image.load(
                'graphics/fruits/apple.png').convert_alpha()
        elif type == 'banana':
            self.image = pygame.image.load(
                'graphics/fruits/banana.png').convert_alpha()
        elif type == 'grape':
            self.image = pygame.image.load(
                'graphics/fruits/grape.png').convert_alpha()
        elif type == 'orange':
            self.image = pygame.image.load(
                'graphics/fruits/orange.png').convert_alpha()
        elif type == 'pear':
            self.image = pygame.image.load(
                'graphics/fruits/pear.png').convert_alpha()
        
        self.rect = self.image.get_rect(  # Place x randomly between 0 and 1280.
            midbottom = (randint(int(128 / 2), int(1280 - 128 / 2)), 0))

        # Movement variable
        self.speed = fall_speed
    
    # Called by game loop (movement)
    def update(self):
        self.rect.y += self.speed
    
    # Called by game loop (player catches or misses fruit)
    def destroy(self):
        self.kill()



# GAMEPLAY FUNCTIONS

# Show the score, # of lives, and current level at the top of the screen
def display_score():
    score_surf = game_font.render(f'Score: {score}', False, (0, 0, 0))
    score_rect = score_surf.get_rect(center = (640, 90))
    screen.blit(score_surf, score_rect)

    lives_surf = game_font.render(f'Lives: {lives}', False, (0, 0, 0))
    lives_rect = lives_surf.get_rect(midleft = (120, 90))
    screen.blit(lives_surf, lives_rect)

    level_surf = game_font.render(f'Level: {level + 1}', False, (0, 0, 0))
    level_rect = level_surf.get_rect(center = (640, 135))
    screen.blit(level_surf, level_rect)

# When level increases, speeds will also increase (for difficulty adjustment)
def update_speeds():
    global fruit_frequency, current_walk_speed, current_fruit_speed,\
           player, level

    # By making frequency smaller, the timer is called much faster,
    # which will spawn fruits at a faster rate.
    if level < 11:
        fruit_frequency = 900 - (75 * level)  # as level +, frequency -
    elif level < 30:
        fruit_frequency = 150 - (5 * level)

    pygame.time.set_timer(fruit_timer, fruit_frequency)

    # Update speed variables with respect to frequency (aka how long it will
    # take for a fruit to reach the ground).
    current_walk_speed = (1280 - player.rect.width) / (2 * fruit_frequency)\
                            * (1000 / 60)
    current_fruit_speed = (720 - player.rect.height) / (2.5 * fruit_frequency)\
                            * (1000 / 60)
    player.set_speed(current_walk_speed)

# Reset global variables + player position
def reset_game():
    global score, lives, level, level_score, game_active
    score = 0
    lives = 3
    level = 0
    level_score = 0
    player.rect.x = 640 - (player.rect.width / 2)
    player.image = player.player_face[1]
    update_speeds()
    game_active = True



# INITIALIZE GAME

# Create screen + clock
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Font
game_font = pygame.font.Font('font/Pixeltype.ttf', 50)

# Sounds
catch_sound = pygame.mixer.Sound('audio/catch.wav')
catch_sound.set_volume(0.05)

miss_sound = pygame.mixer.Sound('audio/miss.wav')
miss_sound.set_volume(0.075)

level_sound = pygame.mixer.Sound('audio/level.wav')
level_sound.set_volume(0.10)

bg_music = pygame.mixer.Sound('audio/Nekomata Master - Far east nightbird.mp3')
bg_music.set_volume(0.05)
bg_music.play(loops = -1)

# Groups
player = Player()
player_group = pygame.sprite.GroupSingle()
player_group.add(player)

fruits = []

# Background
bg_image = pygame.image.load('graphics/background.png')



# INTRO SCREEN

# Player image
player_stand = pygame.image.load(
    'graphics/player/player_face_right.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 1.5)
player_stand_rect = player_stand.get_rect(center = (640, 360))

# Game title
game_name = game_font.render('Fruit Catcher', False, (0, 0, 0))
game_name_rect = game_name.get_rect(center = (640, 144))

# Starting message
game_message = game_font.render('Press SPACE to start', False, (0, 0, 0))
game_message_rect = game_message.get_rect(center = (640, 576))



# GLOBAL VARIABLES

# Timer
fruit_timer = pygame.USEREVENT + 1
fruit_frequency = 1200
pygame.time.set_timer(fruit_timer, fruit_frequency)

# Speed variables
current_walk_speed = (1280 - player.rect.width) / (2 * fruit_frequency)\
                        * (1000 / 60)
current_fruit_speed = (720 - player.rect.height) / (4 * fruit_frequency)\
                        * (1000 / 60)

# Gameplay
game_active = False
score = -1
lives = 3
level = 0
level_score = 0  # require 5 more fruits per level



# GAME LOOP

while True:
    # EVENTS
    for event in pygame.event.get():
        # Exit
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        # Spawn fruits
        if game_active and event.type == fruit_timer:
                
            new_fruit = Fruit(
                choice(['apple', 'banana', 'grape', 'orange', 'pear']),
                current_fruit_speed)
            
            # Sprites need to be in groups to be drawn on the screen
            fruit_group = pygame.sprite.GroupSingle()
            fruit_group.add(new_fruit)
            fruits.insert(0, fruit_group)

        # Intro screen (start button)
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                reset_game()
    
    # ANIMATIONS
    if game_active:
        # Background + score
        screen.blit(bg_image, (0, 0))
        display_score()

        # Player
        player_group.draw(screen)
        player_group.update()

        # Fruits
        for fruit_group in fruits:
            fruit_group.draw(screen)
            fruit_group.update()

            # CATCH
            if pygame.sprite.collide_rect(player, fruit_group.sprite):
                catch_sound.play()

                # Delete fruit
                fruits.remove(fruit_group)
                fruit_group.sprite.destroy()

                # Increase score
                score += 1
                level_score += 1

                # Reach number of fruits needed to go to next level
                if level_score % (10 + (level * 5)) == 0:
                    level_score = 0
                    level += 1
                    level_sound.play()

                    update_speeds()  # increase speed (difficulty)
            
            # MISS
            elif fruit_group.sprite.rect.top > 720:
                miss_sound.play()

                fruits.remove(fruit_group)
                fruit_group.sprite.destroy()

                lives -= 1
                if lives == 0:
                    game_active = False
    
    # INTRO SCREEN
    else:
        # Background
        screen.fill((192, 232, 236))
        screen.blit(player_stand, player_stand_rect)
        screen.blit(game_name, game_name_rect)

        # Delete all fruits
        for fruit_group in fruits:
            fruits.remove(fruit_group)
            fruit_group.sprite.destroy()

        # When game first starts, give starting message
        if score == -1:
            screen.blit(game_message, game_message_rect)
        
        # When game ends, give score
        else:
            score_message = game_font.render(
                f'Your score: {score}', False, (0, 0, 0))
            score_message_rect = score_message.get_rect(center = (640, 576))
            screen.blit(score_message, score_message_rect)
    
    # CLOCK
    pygame.display.update()
    clock.tick(60)