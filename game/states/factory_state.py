import math

import pygame

from game import settings
from game.states.base_state import BaseState


class FactoryState(BaseState):
    """
    Shows the shared factories in a ring with an open center, each
    holding settings.FACTORY_TILE_COUNT randomly-colored tiles. Holds a
    reference to the PlayState instance that created them, so this
    screen never generates its own data — it only reads/mutates
    play_state.factories/center_tiles/players/turn_count. Switching
    back to the boards hands control to that exact same PlayState
    instance, so nothing is rebuilt or reset.

    Has two internal modes (not separate states, since they share all
    the same selection data):
      - "ring": all factories shown in the ring. Click one to select
        it (highlighted light blue), then click "Select Factory" to
        move to "choosing_color".
      - "choosing_color": the selected factory is enlarged in the
        top-left; the rest of the ring shifts right to make room.
        Click a tile to pick its color (highlighting every tile of
        that color), then "Choose Color" to confirm — matching tiles
        are removed from the factory and the rest move to the center
        pool — or "Cancel" to go back without taking anything.
    """

    def __init__(self, app, play_state):
        super().__init__(app)
        self.play_state = play_state

        self.hud_font = pygame.font.SysFont(None, 30)
        self.button_font = pygame.font.SysFont(None, 28)
        self.label_font = pygame.font.SysFont(None, 32)

        self.mode = "ring"
        self.selected_factory_index = None
        self.selected_color = None

        self.center = (
            settings.SCREEN_WIDTH // 2,
            settings.HUD_HEIGHT
            + (settings.SCREEN_HEIGHT - settings.HUD_HEIGHT - settings.BUTTON_AREA_HEIGHT) // 2,
        )
        self.center_shifted = (self.center[0] + settings.FACTORY_RING_SHIFT_X, self.center[1])

        button_row_y = (
            settings.SCREEN_HEIGHT
            - settings.BUTTON_AREA_HEIGHT // 2
            - 23
        )
        self.board_view_button = pygame.Rect(0, 0, 220, 46)
        self.board_view_button.center = (settings.SCREEN_WIDTH // 2, button_row_y + 23)

        self.select_factory_button = pygame.Rect(settings.MARGIN, button_row_y, 200, 46)
        self.cancel_button = pygame.Rect(settings.MARGIN, button_row_y, 150, 46)
        self.choose_color_button = pygame.Rect(settings.MARGIN + 150 + 20, button_row_y, 190, 46)

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _disc_centers(self, ring_center, count):
        """Evenly spaces `count` positions around a circle centered on
        ring_center, starting at the top and going clockwise."""
        centers = []
        for i in range(count):
            angle = (2 * math.pi * i / count) - (math.pi / 2)
            x = ring_center[0] + settings.FACTORY_RING_RADIUS * math.cos(angle)
            y = ring_center[1] + settings.FACTORY_RING_RADIUS * math.sin(angle)
            centers.append((round(x), round(y)))
        return centers

    def _is_hovered(self, rect):
        return rect.collidepoint(pygame.mouse.get_pos())

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from game.states.pause_state import PauseState
                self.app.change_state(PauseState(self.app, self))
                return

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.board_view_button.collidepoint(event.pos):
                    self.app.change_state(self.play_state)
                elif self.mode == "ring":
                    self._handle_ring_click(event.pos)
                elif self.mode == "choosing_color":
                    self._handle_choosing_color_click(event.pos)

    def _handle_ring_click(self, pos):
        if self.select_factory_button.collidepoint(pos):
            if self.selected_factory_index is not None:
                self.mode = "choosing_color"
                self.selected_color = None
            return

        centers = self._disc_centers(self.center, len(self.play_state.factories))
        for i, center in enumerate(centers):
            factory = self.play_state.factories[i]
            if not factory.tiles:
                continue  # empty factories aren't selectable
            if math.hypot(pos[0] - center[0], pos[1] - center[1]) <= settings.FACTORY_DISC_RADIUS:
                # Clicking the already-selected disc deselects it.
                self.selected_factory_index = None if i == self.selected_factory_index else i
                return

    def _handle_choosing_color_click(self, pos):
        if self.cancel_button.collidepoint(pos):
            self._return_to_ring(clear_selection=True)
            return

        if self.choose_color_button.collidepoint(pos) and self.selected_color is not None:
            self._confirm_color_choice()
            return

        factory = self.play_state.factories[self.selected_factory_index]
        tile_size = settings.FACTORY_ENLARGED_TILE_SIZE
        tile_block = 2 * tile_size
        origin_x = settings.FACTORY_ENLARGED_CENTER[0] - tile_block // 2
        origin_y = settings.FACTORY_ENLARGED_CENTER[1] - tile_block // 2

        for i, color in enumerate(factory.tiles):
            row, col = divmod(i, 2)
            tile_rect = pygame.Rect(
                origin_x + col * tile_size, origin_y + row * tile_size, tile_size, tile_size
            )
            if tile_rect.collidepoint(pos):
                self.selected_color = color
                return

    def _confirm_color_choice(self):
        factory = self.play_state.factories[self.selected_factory_index]
        _taken, remaining = factory.take_color(self.selected_color)
        self.play_state.center_tiles.extend(remaining)
        self.play_state.pass_turn()
        self._return_to_ring(clear_selection=True)

    def _return_to_ring(self, clear_selection):
        self.mode = "ring"
        if clear_selection:
            self.selected_factory_index = None
            self.selected_color = None

    def update(self, dt):
        pass

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, screen):
        screen.fill(settings.BLACK)

        active_player = self.play_state.players[self.play_state.current_player_index]
        hud_surf = self.hud_font.render(
            f"Turn {self.play_state.turn_count} \u2014 {active_player.name}'s turn   (ESC: pause)",
            True, settings.WHITE,
        )
        screen.blit(hud_surf, (settings.BOARD_ORIGIN_X, 16))

        if self.mode == "ring":
            self._draw_ring_mode(screen)
        else:
            self._draw_choosing_color_mode(screen)

        self._draw_action_button(screen, self.board_view_button, "Player Boards")

    def _draw_ring_mode(self, screen):
        centers = self._disc_centers(self.center, len(self.play_state.factories))
        for i, (factory, center) in enumerate(zip(self.play_state.factories, centers)):
            is_selected = i == self.selected_factory_index
            self._draw_factory_disc(
                screen, factory, center, settings.FACTORY_DISC_RADIUS,
                settings.FACTORY_TILE_SIZE, highlighted=is_selected,
            )

        self._draw_center_tiles(screen, self.center)

        if self.selected_factory_index is not None:
            self._draw_action_button(screen, self.select_factory_button, "Select Factory")

    def _draw_choosing_color_mode(self, screen):
        factories = self.play_state.factories
        centers = self._disc_centers(self.center_shifted, len(factories))
        for i, (factory, center) in enumerate(zip(factories, centers)):
            if i == self.selected_factory_index:
                continue  # drawn enlarged separately, below
            self._draw_factory_disc(
                screen, factory, center, settings.FACTORY_DISC_RADIUS,
                settings.FACTORY_TILE_SIZE, highlighted=False,
            )

        self._draw_center_tiles(screen, self.center_shifted)

        selected_factory = factories[self.selected_factory_index]
        self._draw_factory_disc(
            screen, selected_factory, settings.FACTORY_ENLARGED_CENTER,
            settings.FACTORY_ENLARGED_RADIUS, settings.FACTORY_ENLARGED_TILE_SIZE,
            highlighted=False, selected_color=self.selected_color,
        )

        label_surf = self.label_font.render("Choose one color", True, settings.WHITE)
        label_rect = label_surf.get_rect(
            center=(
                settings.FACTORY_ENLARGED_CENTER[0],
                settings.FACTORY_ENLARGED_CENTER[1] - settings.FACTORY_ENLARGED_RADIUS - 30,
            )
        )
        screen.blit(label_surf, label_rect)

        self._draw_action_button(screen, self.cancel_button, "Cancel")
        choose_enabled = self.selected_color is not None
        self._draw_action_button(screen, self.choose_color_button, "Choose Color", disabled=not choose_enabled)

    def _draw_factory_disc(self, screen, factory, center, disc_radius, tile_size, highlighted, selected_color=None):
        disc_color = settings.FACTORY_SELECT_HIGHLIGHT if highlighted else settings.DARK_GRAY
        pygame.draw.circle(screen, disc_color, center, disc_radius)
        pygame.draw.circle(screen, settings.GRAY, center, disc_radius, width=2)

        tile_block = 2 * tile_size
        origin_x = center[0] - tile_block // 2
        origin_y = center[1] - tile_block // 2

        for i, color in enumerate(factory.tiles):
            row, col = divmod(i, 2)
            tile_rect = pygame.Rect(
                origin_x + col * tile_size, origin_y + row * tile_size, tile_size, tile_size
            )
            pygame.draw.rect(screen, color, tile_rect)

            is_color_selected = selected_color is not None and color == selected_color
            border_color = settings.FACTORY_SELECT_HIGHLIGHT if is_color_selected else settings.GRAY
            border_width = 5 if is_color_selected else 1
            pygame.draw.rect(screen, border_color, tile_rect, width=border_width)

    def _draw_center_tiles(self, screen, center):
        """
        Draws the leftover center-pool tiles grouped by color — each
        color's tiles sit together (wrapping after
        CENTER_TILES_PER_ROW), with a gap between different colors —
        at the same size as tiles on a factory.
        """
        tiles = self.play_state.center_tiles
        if not tiles:
            return

        size = settings.FACTORY_TILE_SIZE
        per_row = settings.CENTER_TILES_PER_ROW
        gap = settings.CENTER_GROUP_GAP

        groups = []
        for color in settings.COLOR_GRID_PALETTE:
            count = tiles.count(color)
            if count:
                groups.append((color, count))

        group_sizes = []
        for _color, count in groups:
            cols = min(count, per_row)
            rows = -(-count // per_row)  # ceil division
            group_sizes.append((cols * size, rows * size))

        total_width = sum(w for w, _h in group_sizes) + gap * (len(groups) - 1)
        max_height = max(h for _w, h in group_sizes)

        origin_x = center[0] - total_width // 2
        top_y = center[1] - max_height // 2

        x = origin_x
        for (color, count), (group_width, _group_height) in zip(groups, group_sizes):
            for i in range(count):
                row, col = divmod(i, per_row)
                tile_rect = pygame.Rect(x + col * size, top_y + row * size, size, size)
                pygame.draw.rect(screen, color, tile_rect)
                pygame.draw.rect(screen, settings.GRAY, tile_rect, width=1)
            x += group_width + gap

    def _draw_action_button(self, screen, rect, label, disabled=False):
        if disabled:
            color = settings.BUTTON_DISABLED_COLOR
        elif self._is_hovered(rect):
            color = settings.BUTTON_HOVER_COLOR
        else:
            color = settings.BUTTON_COLOR

        pygame.draw.rect(screen, color, rect, border_radius=6)
        text_color = settings.GRAY if disabled else settings.WHITE
        label_surf = self.button_font.render(label, True, text_color)
        label_rect = label_surf.get_rect(center=rect.center)
        screen.blit(label_surf, label_rect)
