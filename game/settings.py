"""All tunable constants live here so you're not hunting through files."""

TITLE = "My Turn-Based Game"
FPS = 60

# --- Players ---
# Everyone plays by the same rules — there's no "enemy," just N players
# taking turns, each marking their own board.
MAX_PLAYERS = 4  # supports 2-4 with the layout math below
DEFAULT_NUM_PLAYERS = 2
PLAYER_COLORS = [
    (70, 130, 220),   # blue
    (220, 60, 60),    # red
    (60, 200, 100),   # green
    (230, 180, 40),   # yellow
]

# --- Each player's personal board ---
BOARD_COLS = 3
BOARD_ROWS = 3
CELL_SIZE = 50
LABEL_HEIGHT = 28  # space above each board for the player's name

BOARD_PIXEL_WIDTH = BOARD_COLS * CELL_SIZE
BOARD_PIXEL_HEIGHT = BOARD_ROWS * CELL_SIZE
BOARD_AREA_WIDTH = BOARD_PIXEL_WIDTH
BOARD_AREA_HEIGHT = LABEL_HEIGHT + BOARD_PIXEL_HEIGHT

# --- Layout of the boards on screen ---
BOARDS_PER_ROW = 2
BOARD_GAP = 30
MARGIN = 20
HUD_HEIGHT = 50
BUTTON_AREA_HEIGHT = 70

_board_cols_used = min(MAX_PLAYERS, BOARDS_PER_ROW)
_board_rows_used = (MAX_PLAYERS + BOARDS_PER_ROW - 1) // BOARDS_PER_ROW

SCREEN_WIDTH = (
    MARGIN * 2
    + _board_cols_used * BOARD_AREA_WIDTH
    + (_board_cols_used - 1) * BOARD_GAP
)
SCREEN_HEIGHT = (
    HUD_HEIGHT
    + MARGIN * 2
    + _board_rows_used * BOARD_AREA_HEIGHT
    + (_board_rows_used - 1) * BOARD_GAP
    + BUTTON_AREA_HEIGHT
)

# Colors (R, G, B)
BLACK = (10, 10, 12)
WHITE = (240, 240, 240)
GRAY = (90, 90, 95)
DARK_GRAY = (35, 35, 40)
BUTTON_COLOR = (70, 130, 220)
BUTTON_HOVER_COLOR = (95, 155, 245)
