"""All tunable constants live here so you're not hunting through files."""
 
TITLE = "My Turn-Based Game"
FPS = 60
 
# --- Fixed window resolution — always 1280x1024, regardless of player count ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024
 
# --- Players ---
# Everyone plays by the same rules — there's no "enemy," just N players
# taking turns, each marking their own board. The actual player count
# is chosen on the menu screen (2 to MAX_PLAYERS) and passed into
# PlayState at runtime.
MAX_PLAYERS = 4
DEFAULT_NUM_PLAYERS = 2
PLAYER_COLORS = [
    (70, 130, 220),   # blue
    (220, 60, 60),    # red
    (60, 200, 100),   # green
    (230, 180, 40),   # yellow
]
 
# --- Fixed palette for the 5x5 color grid (right-hand side of the board) ---
GRID_BLUE = (60, 110, 210)
GRID_YELLOW = (235, 205, 60)
GRID_RED = (200, 60, 60)
GRID_BLACK = (25, 25, 28)
GRID_WHITE = (235, 235, 235)
COLOR_GRID_PALETTE = [GRID_BLUE, GRID_YELLOW, GRID_RED, GRID_BLACK, GRID_WHITE]
 
 
def color_grid_color(row, col):
    """
    The 5x5 grid's fixed color: index = (col - row) % 5 maps into
    COLOR_GRID_PALETTE. This produces 5 diagonal bands of 5 cells each
    (blue starting top-left, then yellow/red/black/white each starting
    one cell further right and wrapping into the bottom-left corner).
    """
    return COLOR_GRID_PALETTE[(col - row) % len(COLOR_GRID_PALETTE)]
 
 
# --- Each player's board layout ---
CELL_SIZE = 50
 
PYRAMID_ROWS = 5           # left-hand grid: row i (1-indexed) has i cells
COLOR_GRID_SIZE = 5        # right-hand grid: 5x5
 
# Bottom row: 7 labeled cells, left to right.
BOTTOM_ROW_LABELS = ["-1", "-1", "-2", "-2", "-2", "-3", "-3"]
 
LABEL_HEIGHT = 30          # space above the grids for the player's name
SUBGRID_GAP = 20           # horizontal gap between the pyramid and the color grid
ROW_GAP = 15               # vertical gap between the grids and the bottom row
 
PYRAMID_WIDTH = PYRAMID_ROWS * CELL_SIZE
COLOR_GRID_WIDTH = COLOR_GRID_SIZE * CELL_SIZE
GRIDS_HEIGHT = max(PYRAMID_ROWS, COLOR_GRID_SIZE) * CELL_SIZE
BOTTOM_ROW_WIDTH = len(BOTTOM_ROW_LABELS) * CELL_SIZE
BOTTOM_ROW_HEIGHT = CELL_SIZE
 
BOARD_AREA_WIDTH = PYRAMID_WIDTH + SUBGRID_GAP + COLOR_GRID_WIDTH
BOARD_AREA_HEIGHT = LABEL_HEIGHT + GRIDS_HEIGHT + ROW_GAP + BOTTOM_ROW_HEIGHT
 
# --- Layout of player boards on screen (always sized for MAX_PLAYERS) ---
BOARDS_PER_ROW = 2
BOARD_GAP = 50
MARGIN = 30
HUD_HEIGHT = 60
BUTTON_AREA_HEIGHT = 80
 
_board_cols_used = min(MAX_PLAYERS, BOARDS_PER_ROW)
_board_rows_used = (MAX_PLAYERS + BOARDS_PER_ROW - 1) // BOARDS_PER_ROW
 
_boards_block_width = (
    _board_cols_used * BOARD_AREA_WIDTH + (_board_cols_used - 1) * BOARD_GAP
)
_boards_block_height = (
    _board_rows_used * BOARD_AREA_HEIGHT + (_board_rows_used - 1) * BOARD_GAP
)
 
# Center the block of boards within the fixed 1280x1024 window.
BOARD_ORIGIN_X = (SCREEN_WIDTH - _boards_block_width) // 2
_available_height_for_boards = SCREEN_HEIGHT - HUD_HEIGHT - BUTTON_AREA_HEIGHT
BOARD_ORIGIN_Y = HUD_HEIGHT + max(0, (_available_height_for_boards - _boards_block_height) // 2)
 
# Colors (R, G, B)
BLACK = (10, 10, 12)
WHITE = (240, 240, 240)
GRAY = (90, 90, 95)
DARK_GRAY = (35, 35, 40)
BUTTON_COLOR = (70, 130, 220)
BUTTON_HOVER_COLOR = (0, 255, 0)
BUTTON_DISABLED_COLOR = (55, 55, 60)
