import pygame

from game import settings
from game.states.base_state import BaseState


class PauseState(BaseState):
    """
    Overlays a pause menu on a frozen PlayState. Holds a reference to
    that exact PlayState instance, so "Resume" hands control straight
    back to it with all game state (players, marks, turn count) intact
    — pausing never recreates or resets the game. While paused, input
    only affects this menu; the underlying game receives no events.
    """

    def __init__(self, app, play_state):
        super().__init__(app)
        self.play_state = play_state

        self.title_font = pygame.font.SysFont(None, 48)
        self.option_font = pygame.font.SysFont(None, 30)

        button_width, button_height = 240, 46
        gap = 16
        center_x = settings.SCREEN_WIDTH // 2
        start_y = settings.SCREEN_HEIGHT // 2 - 40

        self.resume_button = pygame.Rect(0, 0, button_width, button_height)
        self.resume_button.center = (center_x, start_y)

        self.settings_button = pygame.Rect(0, 0, button_width, button_height)
        self.settings_button.center = (center_x, start_y + (button_height + gap))

        self.exit_button = pygame.Rect(0, 0, button_width, button_height)
        self.exit_button.center = (center_x, start_y + 2 * (button_height + gap))

        self._hovered_button = None

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._resume()
                return

            elif event.type == pygame.MOUSEMOTION:
                self._hovered_button = self._button_at(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.resume_button.collidepoint(event.pos):
                    self._resume()
                elif self.settings_button.collidepoint(event.pos):
                    pass  # not implemented yet — intentionally does nothing
                elif self.exit_button.collidepoint(event.pos):
                    self._exit_to_menu()

    def _button_at(self, pos):
        for button in (self.resume_button, self.settings_button, self.exit_button):
            if button.collidepoint(pos):
                return button
        return None

    def _resume(self):
        self.app.change_state(self.play_state)

    def _exit_to_menu(self):
        from game.states.menu_state import MenuState
        self.app.change_state(MenuState(self.app))

    def update(self, dt):
        pass

    def draw(self, screen):
        # Draw the frozen game underneath, dim it, then draw the menu on top.
        self.play_state.draw(screen)

        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(settings.BLACK)
        screen.blit(overlay, (0, 0))

        title_surf = self.title_font.render("Paused", True, settings.WHITE)
        title_rect = title_surf.get_rect(
            center=(settings.SCREEN_WIDTH // 2, self.resume_button.top - 50)
        )
        screen.blit(title_surf, title_rect)

        self._draw_button(screen, self.resume_button, "Resume")
        self._draw_button(screen, self.settings_button, "Settings", disabled=True)
        self._draw_button(screen, self.exit_button, "Exit to Main Menu")

    def _draw_button(self, screen, rect, label, disabled=False):
        if disabled:
            color = settings.BUTTON_DISABLED_COLOR
        elif rect is self._hovered_button:
            color = settings.BUTTON_HOVER_COLOR
        else:
            color = settings.BUTTON_COLOR

        pygame.draw.rect(screen, color, rect, border_radius=6)
        text_color = settings.GRAY if disabled else settings.WHITE
        label_surf = self.option_font.render(label, True, text_color)
        label_rect = label_surf.get_rect(center=rect.center)
        screen.blit(label_surf, label_rect)
