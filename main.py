from sys import exit

import pygame

from level import Level, levels
from sprites import SpriteSheet
from tileset import Tile

# --- Constants ---
TILE_SIZE = 16
SCALING_FACTOR = 2
RENDER_TILE_SIZE = TILE_SIZE * SCALING_FACTOR

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 608
BG_COLOR = (20, 20, 30)

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Dungeon Explorer')
clock = pygame.time.Clock()

# --- SPRITE SETUP ---
TILE_MAP_LOADER = SpriteSheet("graphics/tilemap_packed.png", TILE_SIZE, TILE_SIZE, SCALING_FACTOR)
player_sprite = TILE_MAP_LOADER.get_tile(Tile.PLAYER_CHARACTER.value)
wall_sprite = TILE_MAP_LOADER.get_tile(Tile.INTERNAL_WALL_0.value)
ground_sprite = TILE_MAP_LOADER.get_tile(Tile.GROUND.value)

# --- LEVEL SETUP ---
current_level = Level(
    levels['test'],
    screen,
    TILE_MAP_LOADER
)

# --- Game Loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # --- Drawing ---
    screen.fill(BG_COLOR)

    current_level.draw()

    # --- Update ---
    pygame.display.update()
    clock.tick(60)
