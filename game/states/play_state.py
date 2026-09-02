import pygame

from game import settings
from game.states.base_state import BaseState
from game.entities.player import Player


DEFAULT_PLAYER_NAMES = ["Player 1", "Player 2", "Player 3", "Player 4"]


class PlayState(BaseState):
    """
    N players (2 to settings.MAX_PLAYERS, chosen on the menu and passed
    in as num_players), each with their own board. Only the active
    player's board is clickable; clicking one of its cells toggles a
    mark. Turn order only advances when the "Pass Turn" button is
    clicked — nothing happens automatically or on a timer (update(dt)
    is a no-op). The window itself is always sized for MAX_PLAYERS, so
    fewer players just means unused space in the layout — no resizing.
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

        self.board_areas = self._layout_board_areas()

        self.hud_font = pygame.font.SysFont(None, 28)
        self.label_font = pygame.font.SysFont(None, 24)
        self.button_font = pygame.font.SysFont(None, 30)

        button_width, button_height = 200, 40
        button_x = (settings.SCREEN_WIDTH - button_width) // 2
        button_y = (
            settings.SCREEN_HEIGHT
            - settings.BUTTON_AREA_HEIGHT // 2
            - button_height // 2
        )
        self.pass_turn_button = pygame.Rect(button_x, button_y, button_width, button_height)
        self._button_hovered = False

    def _layout_board_areas(self):
        """One Rect per player (label + grid), arranged left-to-right,
        wrapping after settings.BOARDS_PER_ROW."""
        areas = []
        for i in range(self.num_players):
            col = i % settings.BOARDS_PER_ROW
            row = i // settings.BOARDS_PER_ROW
            x = settings.MARGIN + col * (settings.BOARD_AREA_WIDTH + settings.BOARD_GAP)
            y = (
                settings.HUD_HEIGHT
                + settings.MARGIN
                + row * (settings.BOARD_AREA_HEIGHT + settings.BOARD_GAP)
            )
            areas.append(pygame.Rect(x, y, settings.BOARD_AREA_WIDTH, settings.BOARD_AREA_HEIGHT))
        return areas

    def _grid_rect(self, board_area):
        """The clickable/drawable cell-grid portion of a board area (below its name label)."""
        return pygame.Rect(
            board_area.x,
            board_area.y + settings.LABEL_HEIGHT,
            settings.BOARD_PIXEL_WIDTH,
            settings.BOARD_PIXEL_HEIGHT,
        )

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from game.states.menu_state import MenuState
                self.app.change_state(MenuState(self.app))
                return

            elif event.type == pygame.MOUSEMOTION:
                self._button_hovered = self.pass_turn_button.collidepoint(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.pass_turn_button.collidepoint(event.pos):
                    self._pass_turn()
                else:
                    self._handle_board_click(event.pos)

    def _handle_board_click(self, pos):
        active_board_area = self.board_areas[self.current_player_index]
        grid_rect = self._grid_rect(active_board_area)
        if not grid_rect.collidepoint(pos):
            return  # only the active player's board is interactive

        col = (pos[0] - grid_rect.x) // settings.CELL_SIZE
        row = (pos[1] - grid_rect.y) // settings.CELL_SIZE
        col = max(0, min(settings.BOARD_COLS - 1, col))
        row = max(0, min(settings.BOARD_ROWS - 1, row))

        active_player = self.players[self.current_player_index]
        active_player.toggle_cell(row, col)

    def _pass_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.turn_count += 1

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(settings.BLACK)

        active_player = self.players[self.current_player_index]
        hud_surf = self.hud_font.render(
            f"Turn {self.turn_count} \u2014 {active_player.name}'s turn   (ESC: menu)",
            True, settings.WHITE,
        )
        screen.blit(hud_surf, (settings.MARGIN, 14))

        for player, board_area in zip(self.players, self.board_areas):
            self._draw_player_board(screen, player, board_area)

        self._draw_button(screen)

    def _draw_player_board(self, screen, player, board_area):
        is_active = player.index == self.current_player_index

        label_color = player.color if is_active else settings.GRAY
        label_surf = self.label_font.render(player.name, True, label_color)
        screen.blit(label_surf, (board_area.x, board_area.y))

        grid_rect = self._grid_rect(board_area)
        pygame.draw.rect(screen, settings.DARK_GRAY, grid_rect)

        border_color = player.color if is_active else settings.GRAY
        border_width = 3 if is_active else 1
        pygame.draw.rect(screen, border_color, grid_rect, width=border_width)

        for row in range(settings.BOARD_ROWS):
            for col in range(settings.BOARD_COLS):
                cell_rect = pygame.Rect(
                    grid_rect.x + col * settings.CELL_SIZE,
                    grid_rect.y + row * settings.CELL_SIZE,
                    settings.CELL_SIZE,
                    settings.CELL_SIZE,
                )
                pygame.draw.rect(screen, settings.GRAY, cell_rect, width=1)
                if player.marks[row][col]:
                    inset = cell_rect.inflate(-14, -14)
                    pygame.draw.rect(screen, player.color, inset, border_radius=4)

    def _draw_button(self, screen):
        color = settings.BUTTON_HOVER_COLOR if self._button_hovered else settings.BUTTON_COLOR
        pygame.draw.rect(screen, color, self.pass_turn_button, border_radius=6)
        label_surf = self.button_font.render("Pass Turn", True, settings.WHITE)
        label_rect = label_surf.get_rect(center=self.pass_turn_button.center)
        screen.blit(label_surf, label_rect)
