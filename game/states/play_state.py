import pygame

from game import settings
from game.states.base_state import BaseState
from game.entities.player import Player
from game.entities.factory import Factory


DEFAULT_PLAYER_NAMES = ["Player 1", "Player 2", "Player 3", "Player 4"]


class PlayState(BaseState):
    """
    N players (2 to settings.MAX_PLAYERS, chosen on the menu and passed
    in as num_players), each with their own three-part board: a
    right-aligned left-hand pyramid, a right-hand 5x5 color grid, and a
    bottom row of labeled cells. Only the active player's board is
    clickable. Turn order only advances when the "Pass Turn" button is
    clicked — nothing happens automatically or on a timer (update(dt)
    is a no-op). The window is always 1280x1024 and always laid out
    for MAX_PLAYERS, so fewer players just means unused space — no
    resizing.

    Also owns the shared factories (see entities/factory.py) — created
    once here so they're the same data whether you're looking at this
    screen or FactoryState. The "Factories" button switches to that
    screen, passing this exact PlayState instance along so nothing is
    rebuilt or reset when you switch back.
    """

    def __init__(self, app, num_players=None):
        super().__init__(app)

        if num_players is None:
            num_players = settings.DEFAULT_NUM_PLAYERS
        self.num_players = num_players

        self.players = [
            Player(
                index=i,
                name=DEFAULT_PLAYER_NAMES[i],
                color=settings.PLAYER_COLORS[i % len(settings.PLAYER_COLORS)],
            )
            for i in range(self.num_players)
        ]
        self.current_player_index = 0
        self.turn_count = 1

        num_factories = settings.num_factories_for(self.num_players)
        self.factories = [Factory(i) for i in range(num_factories)]
        self.center_tiles = []  # leftover tiles moved here when a factory is picked

        self.board_areas = self._layout_board_areas()

        self.hud_font = pygame.font.SysFont(None, 30)
        self.label_font = pygame.font.SysFont(None, 26)
        self.button_font = pygame.font.SysFont(None, 30)
        self.cell_label_font = pygame.font.SysFont(None, 22)

        self.pass_turn_button, self.factory_view_button = self._layout_buttons()
        self._hovered_button = None

    def _layout_buttons(self):
        button_width, button_height = 220, 46
        gap = 30
        total_width = button_width * 2 + gap
        start_x = (settings.SCREEN_WIDTH - total_width) // 2
        button_y = (
            settings.SCREEN_HEIGHT
            - settings.BUTTON_AREA_HEIGHT // 2
            - button_height // 2
        )
        pass_turn = pygame.Rect(start_x, button_y, button_width, button_height)
        factory_view = pygame.Rect(
            start_x + button_width + gap, button_y, button_width, button_height
        )
        return pass_turn, factory_view

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _layout_board_areas(self):
        """One Rect per player (label + grids + bottom row), arranged
        left-to-right, wrapping after settings.BOARDS_PER_ROW."""
        areas = []
        for i in range(self.num_players):
            col = i % settings.BOARDS_PER_ROW
            row = i // settings.BOARDS_PER_ROW
            x = settings.BOARD_ORIGIN_X + col * (settings.BOARD_AREA_WIDTH + settings.BOARD_GAP)
            y = settings.BOARD_ORIGIN_Y + row * (settings.BOARD_AREA_HEIGHT + settings.BOARD_GAP)
            areas.append(pygame.Rect(x, y, settings.BOARD_AREA_WIDTH, settings.BOARD_AREA_HEIGHT))
        return areas

    def _pyramid_top_left(self, board_area):
        """Top-left corner of the pyramid's bounding box (settings.PYRAMID_ROWS
        cells wide) — individual rows are right-aligned within this box."""
        return (board_area.x, board_area.y + settings.LABEL_HEIGHT)

    def _pyramid_row_origin_x(self, board_area, row_length):
        """Right-aligns a row of `row_length` cells within the pyramid's
        bounding box, e.g. a 1-cell row starts 4 cells in from the left."""
        left_x, _ = self._pyramid_top_left(board_area)
        return left_x + (settings.PYRAMID_ROWS - row_length) * settings.CELL_SIZE

    def _color_grid_rect(self, board_area):
        x = board_area.x + settings.PYRAMID_WIDTH + settings.SUBGRID_GAP
        y = board_area.y + settings.LABEL_HEIGHT
        return pygame.Rect(x, y, settings.COLOR_GRID_WIDTH, settings.GRIDS_HEIGHT)

    def _bottom_row_rect(self, board_area):
        x = board_area.x
        y = board_area.y + settings.LABEL_HEIGHT + settings.GRIDS_HEIGHT + settings.ROW_GAP
        return pygame.Rect(x, y, settings.BOTTOM_ROW_WIDTH, settings.BOTTOM_ROW_HEIGHT)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from game.states.pause_state import PauseState
                self.app.change_state(PauseState(self.app, self))
                return

            elif event.type == pygame.MOUSEMOTION:
                self._hovered_button = self._button_at(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.pass_turn_button.collidepoint(event.pos):
                    self.pass_turn()
                elif self.factory_view_button.collidepoint(event.pos):
                    from game.states.factory_state import FactoryState
                    self.app.change_state(FactoryState(self.app, self))
                else:
                    self._handle_board_click(event.pos)

    def _button_at(self, pos):
        for button in (self.pass_turn_button, self.factory_view_button):
            if button.collidepoint(pos):
                return button
        return None

    def _handle_board_click(self, pos):
        board_area = self.board_areas[self.current_player_index]
        active_player = self.players[self.current_player_index]

        if self._try_click_pyramid(pos, board_area, active_player):
            return
        if self._try_click_color_grid(pos, board_area, active_player):
            return
        self._try_click_bottom_row(pos, board_area, active_player)

    def _try_click_pyramid(self, pos, board_area, player):
        _, top_y = self._pyramid_top_left(board_area)
        for row in range(settings.PYRAMID_ROWS):
            row_length = row + 1
            row_x = self._pyramid_row_origin_x(board_area, row_length)
            row_y = top_y + row * settings.CELL_SIZE
            row_rect = pygame.Rect(
                row_x, row_y, row_length * settings.CELL_SIZE, settings.CELL_SIZE
            )
            if row_rect.collidepoint(pos):
                col = (pos[0] - row_x) // settings.CELL_SIZE
                player.toggle_pyramid_cell(row, col)
                return True
        return False

    def _try_click_color_grid(self, pos, board_area, player):
        grid_rect = self._color_grid_rect(board_area)
        if not grid_rect.collidepoint(pos):
            return False
        col = (pos[0] - grid_rect.x) // settings.CELL_SIZE
        row = (pos[1] - grid_rect.y) // settings.CELL_SIZE
        col = max(0, min(settings.COLOR_GRID_SIZE - 1, col))
        row = max(0, min(settings.COLOR_GRID_SIZE - 1, row))
        player.toggle_color_cell(row, col)
        return True

    def _try_click_bottom_row(self, pos, board_area, player):
        row_rect = self._bottom_row_rect(board_area)
        if not row_rect.collidepoint(pos):
            return False
        col = (pos[0] - row_rect.x) // settings.CELL_SIZE
        col = max(0, min(len(settings.BOTTOM_ROW_LABELS) - 1, col))
        player.toggle_bottom_cell(col)
        return True

    def pass_turn(self):
        """Public — called by this screen's own button, and by
        FactoryState when a color choice is confirmed."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.turn_count += 1

    def update(self, dt):
        pass

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, screen):
        screen.fill(settings.BLACK)

        active_player = self.players[self.current_player_index]
        hud_surf = self.hud_font.render(
            f"Turn {self.turn_count} \u2014 {active_player.name}'s turn   (ESC: pause)",
            True, settings.WHITE,
        )
        screen.blit(hud_surf, (settings.BOARD_ORIGIN_X, 16))

        for player, board_area in zip(self.players, self.board_areas):
            self._draw_player_board(screen, player, board_area)

        self._draw_action_button(screen, self.pass_turn_button, "Pass Turn")
        self._draw_action_button(screen, self.factory_view_button, "Factories")

    def _draw_player_board(self, screen, player, board_area):
        is_active = player.index == self.current_player_index

        label_color = player.color if is_active else settings.GRAY
        label_surf = self.label_font.render(player.name, True, label_color)
        screen.blit(label_surf, (board_area.x, board_area.y))

        self._draw_pyramid(screen, player, board_area, is_active)
        self._draw_color_grid(screen, player, board_area, is_active)
        self._draw_bottom_row(screen, player, board_area, is_active)

    def _draw_pyramid(self, screen, player, board_area, is_active):
        _, top_y = self._pyramid_top_left(board_area)
        for row in range(settings.PYRAMID_ROWS):
            row_length = row + 1
            row_x = self._pyramid_row_origin_x(board_area, row_length)
            for col in range(row_length):
                cell_rect = pygame.Rect(
                    row_x + col * settings.CELL_SIZE,
                    top_y + row * settings.CELL_SIZE,
                    settings.CELL_SIZE,
                    settings.CELL_SIZE,
                )
                marked = player.pyramid_marks[row][col]
                fill_color = player.color if marked else settings.DARK_GRAY
                pygame.draw.rect(screen, fill_color, cell_rect)
                border_color = player.color if is_active else settings.GRAY
                pygame.draw.rect(screen, border_color, cell_rect, width=1)

    def _draw_color_grid(self, screen, player, board_area, is_active):
        grid_rect = self._color_grid_rect(board_area)
        for row in range(settings.COLOR_GRID_SIZE):
            for col in range(settings.COLOR_GRID_SIZE):
                cell_rect = pygame.Rect(
                    grid_rect.x + col * settings.CELL_SIZE,
                    grid_rect.y + row * settings.CELL_SIZE,
                    settings.CELL_SIZE,
                    settings.CELL_SIZE,
                )
                pygame.draw.rect(screen, settings.color_grid_color(row, col), cell_rect)

                marked = player.color_grid_marks[row][col]
                border_width = 4 if marked else 1
                border_color = player.color if marked else settings.GRAY
                pygame.draw.rect(screen, border_color, cell_rect, width=border_width)

    def _draw_bottom_row(self, screen, player, board_area, is_active):
        row_rect = self._bottom_row_rect(board_area)
        for col, label in enumerate(settings.BOTTOM_ROW_LABELS):
            cell_rect = pygame.Rect(
                row_rect.x + col * settings.CELL_SIZE,
                row_rect.y,
                settings.CELL_SIZE,
                settings.CELL_SIZE,
            )
            marked = player.bottom_row_marks[col]
            fill_color = player.color if marked else settings.DARK_GRAY
            pygame.draw.rect(screen, fill_color, cell_rect)
            border_color = player.color if is_active else settings.GRAY
            pygame.draw.rect(screen, border_color, cell_rect, width=1)

            label_surf = self.cell_label_font.render(label, True, settings.WHITE)
            label_rect = label_surf.get_rect(center=cell_rect.center)
            screen.blit(label_surf, label_rect)

    def _draw_action_button(self, screen, rect, label):
        color = settings.BUTTON_HOVER_COLOR if rect is self._hovered_button else settings.BUTTON_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=6)
        label_surf = self.button_font.render(label, True, settings.WHITE)
        label_rect = label_surf.get_rect(center=rect.center)
        screen.blit(label_surf, label_rect)
