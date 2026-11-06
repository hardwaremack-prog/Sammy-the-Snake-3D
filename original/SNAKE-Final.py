import pygame
import random
import json
import os
import time
import platform
import asyncio
import math
import numpy as np
import ctypes
# Window setup
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
pygame.init()
WIDTH, HEIGHT = 1600, 800
GAMEPLAY_WIDTH, TEXT_WIDTH = 1200, 400
GRID_SIZE = 40
GRID_WIDTH, GRID_HEIGHT = GAMEPLAY_WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE
BASE_FPS = {'Easy': 5, 'Medium': 10, 'Hard': 15}
FPS = BASE_FPS['Medium']
# Colors
COLORS = {
    'BLACK': (0, 0, 0), 'WHITE': (255, 255, 255), 'RED': (255, 0, 0), 'GREEN': (0, 255, 0),
    'GRAY': (100, 100, 100), 'DARK_GRAY': (50, 50, 50, 100), 'YELLOW': (255, 255, 0),
    'BLUE': (0, 0, 255), 'PURPLE': (128, 0, 128), 'BROWN': (139, 69, 19), 'LETTUCE': (0, 128, 0),
    'MAYO': (255, 245, 220), 'CHEESE': (255, 204, 0), 'PEPPERONI': (165, 42, 42),
    'ICE_CREAM': (255, 255, 240), 'ORANGE': (255, 165, 0), 'SALAMI': (200, 50, 50),
    'CAT': (200, 200, 200), 'TURTLE': (0, 100, 0), 'BULLDOG': (150, 100, 50)
}
POWER_UP_COLORS = [COLORS['RED'], COLORS['YELLOW'], COLORS['ORANGE'], COLORS['PURPLE']]
# Game variables
EFFECTS_VOLUME = MUSIC_VOLUME = 1.0
death_animation = False
death_alpha = 255
death_animation_start = 0
DEATH_ANIMATION_DURATION = 1.0
particles = []
text_animations = []
munching = False
munch_time = 0
MUNCH_DURATION = 0.3
snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
snake_dir = (1, 0)
SANDWICH_TYPES = [
    ('mcchicken', lambda s, x, y, size: [
        pygame.draw.circle(s, COLORS['BROWN'], (x + size * 0.5, y + size * 0.7), size * 0.45),
        pygame.draw.circle(s, (210, 180, 140), (x + size * 0.5, y + size * 0.5), size * 0.35),
        pygame.draw.rect(s, COLORS['LETTUCE'], (x + size * 0.3, y + size * 0.3, size * 0.4, size * 0.1)),
        pygame.draw.rect(s, COLORS['MAYO'], (x + size * 0.35, y + size * 0.4, size * 0.3, size * 0.05)),
        pygame.draw.circle(s, COLORS['BROWN'], (x + size * 0.5, y + size * 0.3), size * 0.45)
    ]),
    ('pepperoni_pizza', lambda s, x, y, size: [
        pygame.draw.circle(s, COLORS['BROWN'], (x + size * 0.5, y + size * 0.5), size * 0.45),
        pygame.draw.circle(s, COLORS['RED'], (x + size * 0.5, y + size * 0.5), size * 0.4),
        pygame.draw.circle(s, COLORS['CHEESE'], (x + size * 0.5, y + size * 0.5), size * 0.35),
        [pygame.draw.circle(s, COLORS['PEPPERONI'], (x + size * offset[0], y + size * offset[1]), size * 0.1)
         for offset in [(0.2, 0.2), (0.6, 0.2), (0.4, 0.4), (0.2, 0.6), (0.6, 0.6)]]
    ]),
    ('ice_cream_sandwich', lambda s, x, y, size: [
        pygame.draw.rect(s, COLORS['BROWN'], (x + size * 0.1, y + size * 0.2, size * 0.8, size * 0.15)),
        pygame.draw.rect(s, COLORS['BROWN'], (x + size * 0.1, y + size * 0.65, size * 0.8, size * 0.15)),
        pygame.draw.rect(s, COLORS['ICE_CREAM'], (x + size * 0.1, y + size * 0.35, size * 0.8, size * 0.3))
    ]),
    ('salami_sub', lambda s, x, y, size: [
        pygame.draw.rect(s, COLORS['BROWN'], (x + size * 0.1, y + size * 0.2, size * 0.8, size * 0.6)),
        pygame.draw.circle(s, COLORS['SALAMI'], (x + size * 0.3, y + size * 0.5), size * 0.15),
        pygame.draw.circle(s, COLORS['SALAMI'], (x + size * 0.5, y + size * 0.5), size * 0.15),
        pygame.draw.circle(s, COLORS['SALAMI'], (x + size * 0.7, y + size * 0.5), size * 0.15),
        pygame.draw.rect(s, COLORS['LETTUCE'], (x + size * 0.1, y + size * 0.35, size * 0.8, size * 0.1)),
        pygame.draw.rect(s, COLORS['MAYO'], (x + size * 0.1, y + size * 0.45, size * 0.8, size * 0.05))
    ])
]
food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), random.choice(SANDWICH_TYPES))
POWER_UP_TYPES = [
    ('apple', lambda s, x, y, size: [
        pygame.draw.circle(s, COLORS['RED'], (x + size * 0.5, y + size * 0.5), size * 0.4),
        pygame.draw.rect(s, COLORS['BROWN'], (x + size * 0.45, y + size * 0.2, size * 0.1, size * 0.2))
    ], 0),
    ('banana', lambda s, x, y, size: [
        pygame.draw.polygon(s, COLORS['YELLOW'], [
            (x + size * 0.3, y + size * 0.8), (x + size * 0.5, y + size * 0.2), (x + size * 0.7, y + size * 0.8)]),
        pygame.draw.polygon(s, COLORS['BROWN'], [
            (x + size * 0.5, y + size * 0.2), (x + size * 0.45, y + size * 0.15), (x + size * 0.55, y + size * 0.15)])
    ], 1),
    ('orange', lambda s, x, y, size: [
        pygame.draw.circle(s, COLORS['ORANGE'], (x + size * 0.5, y + size * 0.5), size * 0.4),
        pygame.draw.circle(s, COLORS['GREEN'], (x + size * 0.5, y + size * 0.3), size * 0.05)
    ], 2),
    ('grape', lambda s, x, y, size: [
        pygame.draw.circle(s, COLORS['PURPLE'], (x + size * offset[0], y + size * offset[1]), size * 0.15)
        for offset in [(0.3, 0.3), (0.5, 0.3), (0.4, 0.5), (0.6, 0.5)]
    ] + [pygame.draw.rect(s, COLORS['BROWN'], (x + size * 0.45, y + size * 0.2, size * 0.1, size * 0.2))], 3)
]
OBSTACLE_TYPES = [
    ('cat', lambda s, x, y, size: [
        pygame.draw.circle(s, COLORS['CAT'], (x + size * 0.5, y + size * 0.5), size * 0.4),
        pygame.draw.circle(s, COLORS['BLACK'], (x + size * 0.4, y + size * 0.4), size * 0.05),
        pygame.draw.circle(s, COLORS['BLACK'], (x + size * 0.6, y + size * 0.4), size * 0.05)
    ]),
    ('turtle', lambda s, x, y, size: [
        pygame.draw.rect(s, COLORS['TURTLE'], (x + size * 0.2, y + size * 0.2, size * 0.6, size * 0.6)),
        pygame.draw.circle(s, COLORS['BROWN'], (x + size * 0.5, y + size * 0.3), size * 0.2)
    ]),
    ('bulldog', lambda s, x, y, size: [
        pygame.draw.rect(s, COLORS['BULLDOG'], (x + size * 0.2, y + size * 0.3, size * 0.6, size * 0.5)),
        pygame.draw.circle(s, COLORS['BLACK'], (x + size * 0.35, y + size * 0.4), size * 0.05),
        pygame.draw.circle(s, COLORS['BLACK'], (x + size * 0.65, y + size * 0.4), size * 0.05)
    ])
]
food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), random.choice(SANDWICH_TYPES))
power_up = None
obstacles = []
power_up_active = False
power_up_type = 0
power_up_end_time = 0
score = 0
lives = 3
high_scores = [("Anonymous", 0)] * 5
game_over = False
menu_active = False
high_score_screen = False
sound_enabled = True
use_wasd = True
difficulty = 'Medium'
ready_prompt = True
name_prompt = False
player_name = ""
input_text = ""
credits = "Created By Charles and Sammy"
current_menu_item = 0
score_multiplier = 1
speed_boost_active = False
paused = False
current_song_index = 0
song_end_time = 0
# Initialize screens
gameplay_screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Sammy the Snake")
if platform.system() == "Windows":
    hwnd = pygame.display.get_wm_info()["window"]
    ctypes.windll.user32.ShowWindow(hwnd, 3)
pygame.display.update()
text_surface = pygame.Surface((TEXT_WIDTH, HEIGHT), pygame.SRCALPHA)
clock = pygame.time.Clock()
# Particle class
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y, self.color = x, y, color
        self.vx, self.vy = random.uniform(-50, 50), random.uniform(-50, 50)
        self.lifetime = random.uniform(0.5, 1.0)
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        return self.lifetime > 0
    def draw(self, surface):
        if self.lifetime > 0:
            alpha = int(255 * self.lifetime / 1.0)
            surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.rect(surf, (*self.color[:3], alpha), (0, 0, 8, 8))
            surface.blit(surf, (int(self.x), int(self.y)))
# Text animation class
class TextAnimation:
    def __init__(self, x, y, text, color, font_size=48):
        self.x, self.y, self.text, self.color = x, y, text, color
        self.font = pygame.font.SysFont(None, font_size)
        self.lifetime = 1.0
    def update(self, dt):
        self.lifetime -= dt
        return self.lifetime > 0
    def draw(self, surface):
        if self.lifetime > 0:
            alpha = int(255 * self.lifetime / 1.0)
            surf = self.font.render(self.text, True, (*self.color[:3], alpha))
            surface.blit(surf, surf.get_rect(center=(self.x, self.y)))
# Text wrapping function
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines, current_line, current_width = [], [], 0
    for word in words:
        word_surface = font.render(word + ' ', True, COLORS['WHITE'])
        word_width = word_surface.get_width()
        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width
        else:
            lines.append(' '.join(current_line))
            current_line, current_width = [word], word_width
    if current_line:
        lines.append(' '.join(current_line))
    return lines
# Sound generation
def generate_sound(freqs, durations, sample_rate=44100, volume=1.0, decay=False, use_square=False):
    sound_data = []
    for freq, dur in zip(freqs, durations):
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        note_data = (np.sign(np.sin(2 * np.pi * freq * t)) if use_square else np.sin(2 * np.pi * freq * t)) * 16383 if freq > 0 else np.zeros(len(t))
        if decay:
            note_data *= np.exp(-t * 4) * (1 - np.exp(-t * 10))
        sound_data.extend(note_data)
    sound_data = np.array(sound_data)
    stereo_data = np.column_stack((sound_data, sound_data)).astype(np.int16)
    sound = pygame.sndarray.make_sound(stereo_data)
    sound.set_volume(volume)
    return sound
SONGS = {
    'arcade_tune': ([523.25, 0, 659.25, 0, 783.99, 0, 1046.50, 0, 880.00, 0, 783.99, 0, 659.25, 0, 523.25, 0, 523.25, 659.25, 783.99, 1046.50],
                    [0.15, 0.05, 0.15, 0.05, 0.15, 0.05, 0.15, 0.1, 0.15, 0.05, 0.15, 0.05, 0.15, 0.05, 0.3, 0.15, 0.15, 0.15, 0.15, 0.15], None, 0.0, 1),
    'ode_to_joy': ([
        (329.63, 0.5), (329.63, 0.5), (349.23, 0.5), (392.00, 0.5), (392.00, 0.5), (349.23, 0.5), (329.63, 0.5), (293.66, 0.5),
        (261.63, 0.5), (261.63, 0.5), (293.66, 0.5), (329.63, 0.5), (329.63, 1.5), (293.66, 0.25), (293.66, 1.0),
        (329.63, 0.5), (329.63, 0.5), (349.23, 0.5), (392.00, 0.5), (392.00, 0.5), (349.23, 0.5), (329.63, 0.5), (293.66, 0.5),
        (261.63, 0.5), (293.66, 0.5), (329.63, 0.5), (329.63, 0.5), (293.66, 1.0)
    ], [
        (110.00, 0.5), (110.00, 0.5), (146.83, 0.5), (146.83, 0.5), (146.83, 0.5), (146.83, 0.5), (110.00, 0.5), (110.00, 0.5),
        (98.00, 0.5), (98.00, 0.5), (110.00, 0.5), (110.00, 0.5), (110.00, 1.5), (110.00, 0.25), (110.00, 1.0),
        (110.00, 0.5), (110.00, 0.5), (146.83, 0.5), (146.83, 0.5), (146.83, 0.5), (146.83, 0.5), (110.00, 0.5), (110.00, 0.5),
        (98.00, 0.5), (110.00, 0.5), (110.00, 0.5), (110.00, 0.5), (110.00, 1.0)
    ], None, 0.05, 4),
    'minuet_in_g': ([
        (392.00, 0.375), (392.00, 0.375), (440.00, 0.375), (493.88, 0.375), (392.00, 0.375), (440.00, 0.375), (392.00, 0.375), (349.23, 0.375),
        (329.63, 0.75), (293.66, 0.375), (329.63, 0.375), (349.23, 0.375), (392.00, 0.75), (523.25, 0.375), (493.88, 0.375), (440.00, 0.375),
        (392.00, 0.375), (349.23, 0.375), (392.00, 0.375), (349.23, 0.375), (329.63, 0.375), (293.66, 0.75)
    ], [
        (196.00, 0.375), (196.00, 0.375), (196.00, 0.375), (196.00, 0.375), (196.00, 0.375), (220.00, 0.375), (220.00, 0.375), (174.61, 0.375),
        (164.81, 0.75), (146.83, 0.375), (146.83, 0.375), (174.61, 0.375), (196.00, 0.75), (196.00, 0.375), (196.00, 0.375), (220.00, 0.375),
        (220.00, 0.375), (174.61, 0.375), (174.61, 0.375), (196.00, 0.375), (196.00, 0.375), (146.83, 0.75)
    ], None, 0.05, 3),
    'spring': ([
        (659.25, 0.3), (659.25, 0.3), (659.25, 0.3), (523.25, 0.3), (587.33, 0.3), (659.25, 0.6), (587.33, 0.3), (523.25, 0.3),
        (440.00, 0.3), (523.25, 0.6), (440.00, 0.3), (523.25, 0.3), (587.33, 0.6), (659.25, 0.3), (739.99, 0.3), (783.99, 0.3),
        (659.25, 0.3), (587.33, 0.3), (523.25, 0.3), (587.33, 0.3), (659.25, 0.6)
    ], [
        (164.81, 0.3), (164.81, 0.3), (164.81, 0.3), (174.61, 0.3), (174.61, 0.3), (164.81, 0.6), (174.61, 0.3), (174.61, 0.3),
        (220.00, 0.3), (220.00, 0.6), (220.00, 0.3), (174.61, 0.3), (164.81, 0.6), (164.81, 0.3), (196.00, 0.3), (196.00, 0.3),
        (164.81, 0.3), (174.61, 0.3), (174.61, 0.3), (164.81, 0.3), (164.81, 0.6)
    ], None, 0.02, 3),
    'yankee_doodle': ([
        (261.63, 0.3), (261.63, 0.3), (293.66, 0.3), (329.63, 0.3), (261.63, 0.3), (329.63, 0.3), (293.66, 0.3), (261.63, 0.3),
        (196.00, 0.3), (220.00, 0.3), (261.63, 0.3), (293.66, 0.3), (261.63, 0.6), (261.63, 0.3), (293.66, 0.3), (329.63, 0.3),
        (261.63, 0.3), (329.63, 0.3), (293.66, 0.3), (261.63, 0.3)
    ], [
        (130.81, 0.3), (130.81, 0.3), (130.81, 0.3), (130.81, 0.3), (130.81, 0.3), (130.81, 0.3), (130.81, 0.3), (130.81, 0.3),
        (98.00, 0.3), (98.00, 0.3), (98.00, 0.3), (98.00, 0.3), (130.81, 0.6), (130.81, 0.3), (130.81, 0.3), (130.81, 0.3),
        (130.81, 0.3), (130.81, 0.3), (130.81, 0.3), (130.81, 0.3)
    ], None, 0.02, 4),
    'mary_had_a_little_lamb': ([
        (329.63, 0.4), (293.66, 0.4), (261.63, 0.4), (293.66, 0.4), (329.63, 0.4), (329.63, 0.4), (329.63, 0.4), (293.66, 0.4),
        (293.66, 0.4), (293.66, 0.4), (329.63, 0.4), (392.00, 0.4), (392.00, 0.4), (329.63, 0.4), (293.66, 0.4), (261.63, 0.4),
        (293.66, 0.4), (329.63, 0.4), (329.63, 0.4), (329.63, 0.4), (329.63, 0.4), (293.66, 0.4), (293.66, 0.4), (329.63, 0.4),
        (293.66, 0.4), (261.63, 0.8), (329.63, 0.4), (293.66, 0.4), (261.63, 0.4), (293.66, 0.4), (329.63, 0.4), (329.63, 0.4),
        (329.63, 0.8)
    ], [
        (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4),
        (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (146.83, 0.4), (146.83, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4),
        (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4),
        (110.00, 0.4), (110.00, 0.8), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4), (110.00, 0.4),
        (110.00, 0.8)
    ], None, 0.02, 2),
    'twinkle_twinkle': ([
        (261.63, 0.4), (261.63, 0.4), (392.00, 0.4), (392.00, 0.4), (440.00, 0.4), (440.00, 0.4), (392.00, 0.8),
        (349.23, 0.4), (349.23, 0.4), (329.63, 0.4), (329.63, 0.4), (293.66, 0.4), (293.66, 0.4), (261.63, 0.8),
        (392.00, 0.4), (392.00, 0.4), (349.23, 0.4), (349.23, 0.4), (329.63, 0.4), (329.63, 0.4), (293.66, 0.8),
        (392.00, 0.4), (392.00, 0.4), (349.23, 0.4), (349.23, 0.4), (329.63, 0.4), (329.63, 0.4), (293.66, 0.8),
        (261.63, 0.4), (261.63, 0.4), (392.00, 0.4), (392.00, 0.4), (440.00, 0.4), (440.00, 0.4), (392.00, 0.8),
        (349.23, 0.4), (349.23, 0.4), (329.63, 0.4), (329.63, 0.4), (293.66, 0.4), (293.66, 0.4), (261.63, 0.8)
    ], [
        (130.81, 0.4), (130.81, 0.4), (130.81, 0.4), (130.81, 0.4), (87.31, 0.4), (87.31, 0.4), (87.31, 0.8),
        (87.31, 0.4), (87.31, 0.4), (130.81, 0.4), (130.81, 0.4), (130.81, 0.4), (130.81, 0.4), (130.81, 0.8),
        (130.81, 0.4), (130.81, 0.4), (87.31, 0.4), (87.31, 0.4), (130.81, 0.4), (130.81, 0.4), (130.81, 0.8),
        (130.81, 0.4), (130.81, 0.4), (87.31, 0.4), (87.31, 0.4), (130.81, 0.4), (130.81, 0.4), (130.81, 0.8),
        (130.81, 0.4), (130.81, 0.4), (130.81, 0.4), (130.81, 0.4), (87.31, 0.4), (87.31, 0.4), (87.31, 0.8),
        (87.31, 0.4), (87.31, 0.4), (130.81, 0.4), (130.81, 0.4), (130.81, 0.4), (130.81, 0.4), (130.81, 0.8)
    ], None, 0.02, 6),
    'frere_jacques': ([
        (261.63, 0.4), (293.66, 0.4), (329.63, 0.4), (261.63, 0.4), # C, D, E, C
        (261.63, 0.4), (293.66, 0.4), (329.63, 0.4), (261.63, 0.4), # C, D, E, C
        (329.63, 0.4), (349.23, 0.4), (392.00, 0.8), # E, F, G
        (329.63, 0.4), (349.23, 0.4), (392.00, 0.8), # E, F, G
        (392.00, 0.4), (440.00, 0.4), (392.00, 0.4), (349.23, 0.4), (329.63, 0.4), (261.63, 0.4), # G, A, G, F, E, C
        (392.00, 0.4), (440.00, 0.4), (392.00, 0.4), (349.23, 0.4), (329.63, 0.4), (261.63, 0.4), # G, A, G, F, E, C
        (261.63, 0.4), (392.00, 0.4), (261.63, 0.8), # C, G, C
        (261.63, 0.4), (392.00, 0.4), (261.63, 0.8) # C, G, C
    ], [
        (130.81, 0.4), (130.81, 0.4), (130.81, 0.4), (130.81, 0.4),
        (130.81, 0.4), (130.81, 0.4), (130.81, 0.4), (130.81, 0.4),
        (174.61, 0.4), (174.61, 0.4), (174.61, 0.8),
        (174.61, 0.4), (174.61, 0.4), (174.61, 0.8),
        (196.00, 0.4), (196.00, 0.4), (196.00, 0.4), (174.61, 0.4), (130.81, 0.4), (130.81, 0.4),
        (196.00, 0.4), (196.00, 0.4), (196.00, 0.4), (174.61, 0.4), (130.81, 0.4), (130.81, 0.4),
        (130.81, 0.4), (174.61, 0.4), (130.81, 0.8),
        (130.81, 0.4), (174.61, 0.4), (130.81, 0.8)
    ], None, 0.02, 4)
}
def generate_music(song_name):
    song_data = SONGS[song_name]
    sample_rate = 44100
    sound_data = []
    if song_name == 'arcade_tune':
        freqs, durations, _, _, repeats = song_data
        for _ in range(repeats):
            for freq, dur in zip(freqs, durations):
                t = np.linspace(0, dur, int(sample_rate * dur), False)
                note_data = np.sin(2 * np.pi * freq * t) * 16383 if freq > 0 else np.zeros(len(t))
                note_data *= np.exp(-t * 3) * (1 - np.exp(-t * 10))
                sound_data.extend(note_data)
    else:
        bass_notes, melody_notes, harmony_notes, pause_duration, repeats = song_data
        for _ in range(repeats):
            for i in range(len(bass_notes)):
                t = np.linspace(0, bass_notes[i][1], int(sample_rate * bass_notes[i][1]), False)
                bass_freq = bass_notes[i][0]
                melody_freq = melody_notes[i % len(melody_notes)][0] if i < len(melody_notes) else 0
                harmony_freq = harmony_notes[i % len(harmony_notes)][0] if harmony_notes else 0
                note_data = (np.sin(2 * np.pi * bass_freq * t) * 0.5 +
                             np.sin(2 * np.pi * melody_freq * t) * 0.3 +
                             (np.sin(2 * np.pi * harmony_freq * t) * 0.2 if harmony_notes else 0)) * 16383
                note_data *= np.exp(-t * 3) * (1 - np.exp(-t * 10))
                sound_data.extend(note_data)
                sound_data.extend(np.zeros(int(sample_rate * pause_duration)))
    sound_data = np.array(sound_data)
    stereo_data = np.column_stack((sound_data, sound_data)).astype(np.int16)
    sound = pygame.sndarray.make_sound(stereo_data)
    sound.set_volume(MUSIC_VOLUME)
    return sound
# Load sounds
eat_sound = generate_sound([440], [0.1], volume=EFFECTS_VOLUME)
game_over_sound = generate_sound([220], [0.5], volume=EFFECTS_VOLUME)
power_up_sound = generate_sound([523.25], [0.2], volume=EFFECTS_VOLUME, decay=True)
arcade_tune = generate_music('arcade_tune')
songs = [generate_music(name) for name in SONGS if name != 'arcade_tune']
song_durations = [68.6, 31.4, 23.8, 26.8, 29.3, 120.2, 60.2]
# File path for high scores
HIGH_SCORE_FILE = os.path.expanduser("~/snake_high_scores.json")
def load_high_scores():
    global high_scores
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as f:
                high_scores = [(item['name'], int(item['score'])) for item in json.load(f)][:5]
                high_scores.extend([("Anonymous", 0)] * (5 - len(high_scores)))
    except (json.JSONDecodeError, IOError):
        pass
def save_high_scores():
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump([{'name': name, 'score': score} for name, score in high_scores], f)
    except IOError:
        pass
def update_high_scores():
    global high_scores
    high_scores.append((player_name or "Anonymous", score))
    high_scores = sorted(high_scores, key=lambda x: x[1], reverse=True)[:5]
    save_high_scores()
def reset_game(keep_score=False):
    global snake, snake_dir, food, power_up, obstacles, power_up_active, power_up_end_time, score, game_over, lives, power_up_type, score_multiplier, speed_boost_active, paused, death_animation, death_alpha, particles, text_animations, munching, munch_time
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    snake_dir = (1, 0)
    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), random.choice(SANDWICH_TYPES))
    power_up = None
    obstacles = []
    for _ in range(3): # Spawn 3 obstacles
        for _ in range(10):
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos != (food[0], food[1]) and pos not in snake and (not power_up or pos != power_up[0]) and pos not in [o[0] for o in obstacles]:
                obstacles.append((pos, random.choice(OBSTACLE_TYPES)))
                break
    power_up_active = False
    power_up_type = 0
    power_up_end_time = 0
    score_multiplier = 1
    speed_boost_active = False
    paused = death_animation = False
    death_alpha = 255
    particles = []
    text_animations = []
    munching = False
    munch_time = 0
    if not keep_score:
        score = 0
        lives = 3
    game_over = False
def spawn_power_up():
    if random.random() < 0.2:
        for _ in range(10):
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos != (food[0], food[1]) and pos not in snake and pos not in [o[0] for o in obstacles]:
                return (pos, random.choice(POWER_UP_TYPES))
    return None
def draw_sammy_graphic(surface, x, y, size):
    head_size = size // 2
    pygame.draw.ellipse(surface, COLORS['GREEN'], (x - head_size // 2, y - head_size // 2, head_size, head_size * 1.2))
    eye_size = head_size // 5
    for offset in [-1, 1]:
        pygame.draw.circle(surface, COLORS['WHITE'], (x + offset * head_size // 4, y - head_size // 4), eye_size)
        pygame.draw.circle(surface, COLORS['BLACK'], (x + offset * head_size // 4, y - head_size // 4), eye_size // 2)
        pygame.draw.rect(surface, COLORS['BLACK'], (x + offset * head_size // 4 - head_size // 6, y - head_size // 4, head_size // 3, head_size // 6))
    pygame.draw.line(surface, COLORS['BLACK'], (x - head_size // 12, y - head_size // 4 + head_size // 12),
                     (x + head_size // 12, y - head_size // 4 + head_size // 12), 2)
    pygame.draw.arc(surface, COLORS['RED'], (x - head_size // 3, y, head_size // 1.5, head_size // 2), 3.14, 6.28, 3)
    segment_size = head_size // 2
    for i in range(3):
        offset_y = head_size // 2 + i * segment_size * 1.2
        offset_x = math.sin(i * 0.5) * segment_size // 2
        pygame.draw.ellipse(surface, COLORS['GREEN'], (x - segment_size // 2 + offset_x, y + offset_y, segment_size, segment_size))
def draw_menu():
    text_surface.fill(COLORS['DARK_GRAY'])
    title_font = pygame.font.SysFont(None, 80)
    font = pygame.font.SysFont(None, 48)
    instruction_font = pygame.font.SysFont(None, 36)
    text_surface.blit(title_font.render("Game Menu", True, COLORS['WHITE']), (TEXT_WIDTH // 2 - 150, 100))
    menu_items = [
        f"Sound: {'On' if sound_enabled else 'Off'}",
        f"Effects Volume: {int(EFFECTS_VOLUME * 100)}%",
        f"Music Volume: {int(MUSIC_VOLUME * 100)}%",
        f"Controls: {'WASD' if use_wasd else 'Arrows'}",
        f"Difficulty: {difficulty}",
        "Return to Game", "Reset Game", "Exit"
    ]
    for i, item in enumerate(menu_items):
        color = COLORS['YELLOW'] if i == current_menu_item else COLORS['WHITE']
        text_surface.blit(font.render(item, True, color), (TEXT_WIDTH // 2 - 150, 200 + i * 50))
    instructions = ["Use UP/DOWN to navigate, ENTER to select", "LEFT/RIGHT to adjust volume", "Press M to close menu"]
    y_offset = 600
    for instruction in instructions:
        for j, line in enumerate(wrap_text(instruction, instruction_font, TEXT_WIDTH - 40)):
            text_surface.blit(instruction_font.render(line, True, COLORS['GRAY']), (TEXT_WIDTH // 2 - 150, y_offset + j * 30))
        y_offset = len(wrap_text(instruction, instruction_font, TEXT_WIDTH - 40)) * 30
    text_surface.blit(instruction_font.render(credits, True, COLORS['GRAY']), (20, HEIGHT - 30))
def draw_ready_prompt():
    gameplay_screen.fill(COLORS['BLACK'])
    title_font = pygame.font.SysFont(None, 80)
    font = pygame.font.SysFont(None, 60)
    label_font = pygame.font.SysFont(None, 36)
    pulse_scale = 1 + 0.1 * math.sin(time.time() * 5)
    item_size = int(60 * pulse_scale)
    item_offset = (60 - item_size) // 2
    draw_sammy_graphic(gameplay_screen, WIDTH // 2, 200, 150)
    obstacle_positions = [(50, 300), (50, 400), (50, 500)]
    obstacle_labels = ["Cat (Danger)", "Turtle (Danger)", "Bulldog (Danger)"]
    for i, (_, draw_func) in enumerate(OBSTACLE_TYPES):
        draw_func(gameplay_screen, obstacle_positions[i][0] - 30 + item_offset, obstacle_positions[i][1] - 30 + item_offset, item_size)
        gameplay_screen.blit(label_font.render(obstacle_labels[i], True, COLORS['WHITE']),
                             (obstacle_positions[i][0] - 50, obstacle_positions[i][1] - 40))
    food_positions = [(200, 650), (350, 650), (500, 650), (650, 650)]
    food_labels = ["McChicken", "Pepperoni Pizza", "Ice Cream Sandwich", "Salami Sub"]
    food_label_y = [610, 690, 610, 690]
    for i, (_, draw_func) in enumerate(SANDWICH_TYPES):
        draw_func(gameplay_screen, food_positions[i][0] - 30 + item_offset, food_positions[i][1] - 30 + item_offset, item_size)
        gameplay_screen.blit(label_font.render(food_labels[i], True, COLORS['WHITE']),
                             (food_positions[i][0] - 50, food_label_y[i]))
    power_up_positions = [(1000, 650), (1150, 650), (1300, 650), (1450, 650)]
    power_up_labels = ["Apple (Slow)", "Banana (+Life)", "Orange (2x Score)", "Grape (Speed)"]
    power_up_label_y = [610, 690, 610, 690]
    for i, (_, draw_func, _) in enumerate(POWER_UP_TYPES):
        draw_func(gameplay_screen, power_up_positions[i][0] - 30 + item_offset, power_up_positions[i][1] - 30 + item_offset, item_size)
        gameplay_screen.blit(label_font.render(power_up_labels[i], True, COLORS['WHITE']),
                             (power_up_positions[i][0] - 50, power_up_label_y[i]))
    texts = [
        (title_font, "Welcome to Sammy", 50),
        (title_font, "the Snake Loves Sandwiches", 110),
        (font, "Are you ready? (Y/N)", 400),
        (font, "Press Y to start, N to quit", 450),
        (font, credits, 500)
    ]
    for font, text, y in texts:
        text_surf = font.render(text, True, COLORS['WHITE' if font != font else 'GRAY'])
        gameplay_screen.blit(text_surf, text_surf.get_rect(center=(WIDTH // 2, y)))
def draw_name_prompt():
    gameplay_screen.fill(COLORS['BLACK'])
    font = pygame.font.SysFont(None, 60)
    prompt_text = f"Enter your name: {input_text}_"
    for i, line in enumerate(wrap_text(prompt_text, font, WIDTH - 40)):
        gameplay_screen.blit(font.render(line, True, COLORS['WHITE']),
                             (WIDTH // 2 - 200, HEIGHT // 2 - len(wrap_text(prompt_text, font, WIDTH - 40)) * 15 + i * 30))
    gameplay_screen.blit(font.render(credits, True, COLORS['GRAY']), (WIDTH // 2 - 200, HEIGHT - 30))
def draw_high_score_screen():
    text_surface.fill(COLORS['DARK_GRAY'])
    font = pygame.font.SysFont(None, 48)
    text_surface.blit(font.render("High Scores", True, COLORS['WHITE']), (TEXT_WIDTH // 2 - 100, 100))
    for i, (name, hs) in enumerate(high_scores):
        for j, line in enumerate(wrap_text(f"{i+1}. {name} - {hs}", font, TEXT_WIDTH - 40)):
            text_surface.blit(font.render(line, True, COLORS['WHITE']), (20, 200 + i * 50 + j * 30))
    text_surface.blit(font.render("Press any key to continue", True, COLORS['WHITE']), (TEXT_WIDTH // 2 - 150, HEIGHT - 100))
def update_volumes():
    for sound in [eat_sound, game_over_sound, power_up_sound, arcade_tune] + songs:
        sound.set_volume(EFFECTS_VOLUME if sound in [eat_sound, game_over_sound, power_up_sound] else MUSIC_VOLUME)
def setup():
    global gameplay_screen
    load_high_scores()
    reset_game()
    gameplay_screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    if platform.system() == "Windows":
        hwnd = pygame.display.get_wm_info()["window"]
        ctypes.windll.user32.ShowWindow(hwnd, 3)
    pygame.display.update()
    if sound_enabled:
        arcade_tune.play()
async def update_loop():
    global snake, snake_dir, food, power_up, obstacles, power_up_active, power_up_end_time, score, game_over, menu_active, sound_enabled, use_wasd, ready_prompt, name_prompt, input_text, player_name, difficulty, lives, high_score_screen, FPS, current_menu_item, power_up_type, score_multiplier, speed_boost_active, paused, current_song_index, song_end_time, death_animation, death_alpha, death_animation_start, particles, text_animations, munching, munch_time, EFFECTS_VOLUME, MUSIC_VOLUME
    dt = 1.0 / FPS
    if munching and time.time() > munch_time + MUNCH_DURATION:
        munching = False
    particles[:] = [p for p in particles if p.update(dt)]
    text_animations[:] = [t for t in text_animations if t.update(dt)]
    if sound_enabled and not any([paused, menu_active, game_over, high_score_screen, ready_prompt, name_prompt]):
        if time.time() >= song_end_time:
            songs[current_song_index].stop()
            current_song_index = (current_song_index + 1) % len(songs)
            songs[current_song_index].play(-1)
            song_end_time = time.time() + song_durations[current_song_index]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return False
        if event.type == pygame.KEYDOWN:
            if ready_prompt:
                if event.key == pygame.K_y:
                    ready_prompt = False
                    name_prompt = True
                elif event.key == pygame.K_n:
                    pygame.quit()
                    return False
            elif name_prompt:
                if event.key == pygame.K_RETURN:
                    player_name = input_text
                    name_prompt = False
                    reset_game()
                    if sound_enabled:
                        songs[current_song_index].play(-1)
                        song_end_time = time.time() + song_durations[current_song_index]
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isalnum() and len(input_text) < 15:
                    input_text += event.unicode
            elif high_score_screen:
                high_score_screen = False
                reset_game()
                if sound_enabled:
                    songs[current_song_index].play(-1)
                    song_end_time = time.time() + song_durations[current_song_index]
            elif game_over and not high_score_screen:
                if event.key == pygame.K_r:
                    reset_game()
                    if sound_enabled:
                        songs[current_song_index].play(-1)
                        song_end_time = time.time() + song_durations[current_song_index]
                elif event.key == pygame.K_q:
                    pygame.quit()
                    return False
            elif menu_active:
                if event.key == pygame.K_UP:
                    current_menu_item = (current_menu_item - 1) % 8
                elif event.key == pygame.K_DOWN:
                    current_menu_item = (current_menu_item + 1) % 8
                elif event.key == pygame.K_RETURN:
                    if current_menu_item == 0:
                        sound_enabled = not sound_enabled
                        update_volumes()
                        if sound_enabled and not paused:
                            songs[current_song_index].play(-1)
                            song_end_time = time.time() + song_durations[current_song_index]
                        elif not sound_enabled:
                            songs[current_song_index].stop()
                    elif current_menu_item == 1:
                        EFFECTS_VOLUME = min(1.0, EFFECTS_VOLUME + 0.1) if EFFECTS_VOLUME < 1.0 else 0.0
                        update_volumes()
                    elif current_menu_item == 2:
                        MUSIC_VOLUME = min(1.0, MUSIC_VOLUME + 0.1) if MUSIC_VOLUME < 1.0 else 0.0
                        update_volumes()
                    elif current_menu_item == 3:
                        use_wasd = not use_wasd
                    elif current_menu_item == 4:
                        difficulties = ['Easy', 'Medium', 'Hard']
                        difficulty = difficulties[(difficulties.index(difficulty) + 1) % 3]
                        FPS = BASE_FPS[difficulty]
                    elif current_menu_item == 5:
                        menu_active = False
                        if sound_enabled and not paused:
                            songs[current_song_index].play(-1)
                            song_end_time = time.time() + song_durations[current_song_index]
                    elif current_menu_item == 6:
                        reset_game()
                        menu_active = False
                        if sound_enabled and not paused:
                            songs[current_song_index].play(-1)
                            song_end_time = time.time() + song_durations[current_song_index]
                    elif current_menu_item == 7:
                        pygame.quit()
                        return False
                elif event.key in [pygame.K_LEFT, pygame.K_RIGHT] and current_menu_item in [1, 2]:
                    delta = 0.1 if event.key == pygame.K_RIGHT else -0.1
                    if current_menu_item == 1:
                        EFFECTS_VOLUME = max(0.0, min(1.0, EFFECTS_VOLUME + delta))
                    else:
                        MUSIC_VOLUME = max(0.0, min(1.0, MUSIC_VOLUME + delta))
                    update_volumes()
            elif event.key == pygame.K_m:
                menu_active = not menu_active
                current_menu_item = 0
                if sound_enabled:
                    songs[current_song_index].stop() if menu_active else songs[current_song_index].play(-1)
                    if not menu_active and not paused:
                        song_end_time = time.time() + song_durations[current_song_index]
            elif event.key == pygame.K_p and not menu_active and not high_score_screen and not game_over:
                paused = not paused
                if sound_enabled:
                    songs[current_song_index].stop() if paused else songs[current_song_index].play(-1)
                    if not paused:
                        song_end_time = time.time() + song_durations[current_song_index]
            elif not any([game_over, high_score_screen, paused, death_animation]) and snake and isinstance(snake_dir, tuple):
                controls = {
                    'wasd': {pygame.K_w: ((0, -1), (0, 1)), pygame.K_s: ((0, 1), (0, -1)), pygame.K_a: ((-1, 0), (1, 0)), pygame.K_d: ((1, 0), (-1, 0))},
                    'arrows': {pygame.K_UP: ((0, -1), (0, 1)), pygame.K_DOWN: ((0, 1), (0, -1)), pygame.K_LEFT: ((-1, 0), (1, 0)), pygame.K_RIGHT: ((1, 0), (-1, 0))}
                }
                control_map = controls['wasd' if use_wasd else 'arrows']
                if event.key in control_map:
                    new_dir, invalid_dir = control_map[event.key]
                    if snake_dir != invalid_dir:
                        snake_dir = new_dir
    effective_fps = FPS * (2 if speed_boost_active else 0.5 if power_up_active and power_up_type == 0 else 1)
    if not any([game_over, high_score_screen, paused, death_animation]) and snake and isinstance(snake_dir, tuple):
        head_x, head_y = snake[0]
        new_head = ((head_x + snake_dir[0]) % GRID_WIDTH, (head_y + snake_dir[1]) % GRID_HEIGHT)
        snake.insert(0, new_head)
        if new_head == (food[0], food[1]):
            score += 10 * score_multiplier
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), random.choice(SANDWICH_TYPES))
            power_up = spawn_power_up()
            if sound_enabled:
                eat_sound.play()
            munching = True
            munch_time = time.time()
            text_animations.append(TextAnimation(TEXT_WIDTH + GAMEPLAY_WIDTH // 2, HEIGHT // 2 - 20, "Good Job", COLORS['YELLOW']))
            for _ in range(2):
                if len(snake) > 1:
                    snake.append(snake[-1])
        else:
            snake.pop()
        if power_up and new_head == power_up[0]:
            power_up_active = True
            power_up_type = power_up[1][2]
            power_up_end_time = time.time() + (5.0 if power_up_type == 3 else 10.0)
            if power_up_type == 1:
                lives = min(lives + 1, 5)
                power_up_active = False
            elif power_up_type == 2:
                score_multiplier = 2
            elif power_up_type == 3:
                speed_boost_active = True
            if sound_enabled:
                power_up_sound.play()
            for _ in range(10):
                particles.append(Particle(power_up[0][0] * GRID_SIZE + GRID_SIZE / 2 + TEXT_WIDTH, power_up[0][1] * GRID_SIZE + GRID_SIZE / 2, POWER_UP_COLORS[power_up_type]))
            power_up = None
        if new_head in snake[1:] or new_head in [o[0] for o in obstacles]:
            lives -= 1
            if lives > 0:
                death_animation = True
                death_animation_start = time.time()
                if sound_enabled:
                    game_over_sound.play()
            else:
                game_over = True
                update_high_scores()
                high_score_screen = True
                if sound_enabled:
                    songs[current_song_index].stop()
        if power_up_active and time.time() > power_up_end_time:
            power_up_active = False
            if power_up_type == 2:
                score_multiplier = 1
            elif power_up_type == 3:
                speed_boost_active = False
    if death_animation:
        elapsed = time.time() - death_animation_start
        if elapsed < DEATH_ANIMATION_DURATION:
            death_alpha = int(255 * (1 - elapsed / DEATH_ANIMATION_DURATION))
        else:
            death_animation = False
            death_alpha = 255
            if lives > 0:
                reset_game(keep_score=True)
            else:
                game_over = True
                update_high_scores()
                high_score_screen = True
                if sound_enabled:
                    songs[current_song_index].stop()
    gameplay_screen.fill(COLORS['BLACK'])
    text_surface.fill(COLORS['DARK_GRAY'])
    if ready_prompt:
        draw_ready_prompt()
    elif name_prompt:
        draw_name_prompt()
    elif menu_active:
        draw_menu()
        gameplay_screen.blit(text_surface, (0, 0))
    elif high_score_screen:
        draw_high_score_screen()
        gameplay_screen.blit(text_surface, (0, 0))
    elif paused:
        font = pygame.font.SysFont(None, 80)
        text_surface.fill(COLORS['DARK_GRAY'])
        text_surface.blit(font.render("Paused - Press P to resume", True, COLORS['WHITE']), (TEXT_WIDTH // 2 - 200, HEIGHT // 2))
        gameplay_screen.blit(text_surface, (0, 0))
    else:
        snake_surface = pygame.Surface((GAMEPLAY_WIDTH, HEIGHT), pygame.SRCALPHA)
        for i, segment in enumerate(snake):
            offset = math.sin(time.time() * 5 + i * 0.5) * 5 if i > 0 else 0
            x, y = segment[0] * GRID_SIZE + offset, segment[1] * GRID_SIZE
            if i == 0:
                scale = 1 + 0.1 * math.sin(time.time() * 3)
                size = int(GRID_SIZE * scale)
                offset_size = (GRID_SIZE - size) // 2
                if munching:
                    pygame.draw.ellipse(snake_surface, (*COLORS['GREEN'][:3], death_alpha), (x + offset_size, y + offset_size, size, size * 1.2))
                    pygame.draw.arc(snake_surface, COLORS['BLACK'], (x + offset_size, y + size * 0.7, size, size * 0.5), 3.14, 6.28, 3)
                else:
                    pygame.draw.rect(snake_surface, (*COLORS['GREEN'][:3], death_alpha), (x + offset_size, y + offset_size, size, size))
            else:
                pygame.draw.rect(snake_surface, (*COLORS['GREEN'][:3], death_alpha), (x, y, GRID_SIZE, GRID_SIZE))
        gameplay_screen.blit(snake_surface, (TEXT_WIDTH, 0))
        pulse_scale = 1 + 0.1 * math.sin(time.time() * 5)
        food_size = int(GRID_SIZE * pulse_scale)
        food_offset = (GRID_SIZE - food_size) // 2
        food[2][1](gameplay_screen, food[0] * GRID_SIZE + food_offset + TEXT_WIDTH, food[1] * GRID_SIZE + food_offset, food_size)
        if power_up:
            power_up[1][1](gameplay_screen, power_up[0][0] * GRID_SIZE + TEXT_WIDTH, power_up[0][1] * GRID_SIZE, GRID_SIZE)
        for obstacle_pos, (name, draw_func) in obstacles:
            draw_func(gameplay_screen, obstacle_pos[0] * GRID_SIZE + TEXT_WIDTH, obstacle_pos[1] * GRID_SIZE, GRID_SIZE)
        header_font = pygame.font.SysFont(None, 48)
        detail_font = pygame.font.SysFont(None, 36)
        text_surface.blit(header_font.render(f"Score: {score}", True, COLORS['WHITE']), (20, 20))
        text_surface.blit(header_font.render(f"Lives: {lives}", True, COLORS['WHITE']), (20, 80))
        if power_up_active or speed_boost_active or score_multiplier > 1:
            remaining_time = max(0, power_up_end_time - time.time())
            bar_width = int((remaining_time / (5.0 if power_up_type == 3 else 10.0)) * 200)
            pygame.draw.rect(text_surface, POWER_UP_COLORS[power_up_type], (20, 140, bar_width, 20))
            pygame.draw.rect(text_surface, COLORS['WHITE'], (20, 140, 200, 20), 2)
        text_surface.blit(header_font.render("High Scores:", True, COLORS['WHITE']), (20, 200))
        for i, (name, hs) in enumerate(high_scores):
            for j, line in enumerate(wrap_text(f"{i+1}. {name} - {hs}", detail_font, TEXT_WIDTH - 40)):
                text_surface.blit(detail_font.render(line, True, COLORS['WHITE']), (20, 240 + i * 50 + j * 30))
        for i, line in enumerate(wrap_text(f"Controls: {'WASD' if use_wasd else 'Arrows'}", detail_font, TEXT_WIDTH - 40)):
            text_surface.blit(detail_font.render(line, True, COLORS['WHITE']), (20, 500 + i * 30))
        for i, line in enumerate(wrap_text(f"Difficulty: {difficulty}", detail_font, TEXT_WIDTH - 40)):
            text_surface.blit(detail_font.render(line, True, COLORS['WHITE']), (20, 560 + i * 30))
        for i, line in enumerate(wrap_text(f"Player: {player_name or 'Anonymous'}", detail_font, TEXT_WIDTH - 40)):
            text_surface.blit(detail_font.render(line, True, COLORS['WHITE']), (20, 620 + i * 30))
        for i, line in enumerate(wrap_text("Press M for menu, P to pause", detail_font, TEXT_WIDTH - 40)):
            text_surface.blit(detail_font.render(line, True, COLORS['WHITE']), (20, 750 + i * 30))
        text_surface.blit(detail_font.render(credits, True, COLORS['GRAY']), (20, HEIGHT - 30))
        gameplay_screen.blit(text_surface, (0, 0))
        for particle in particles:
            particle.draw(gameplay_screen)
        for text_anim in text_animations:
            text_anim.draw(gameplay_screen)
    pygame.display.flip()
    await asyncio.sleep(1.0 / effective_fps)
    clock.tick(FPS)
    return True
async def main():
    setup()
    while await update_loop():
        pass
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())