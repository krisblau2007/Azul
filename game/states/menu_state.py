import pygame

from game import settings
from game.states.base_state import BaseState


PLAYER_COUNT_OPTIONS = list(range(2, settings.MAX_PLAYERS + 1))  # e.g. [2, 3, 4]


class MenuState(BaseState):
    """
    Title screen + player-count picker. The chosen count is passed into
    PlayState when the game starts — nothing about the window size
    changes, only how many players/boards PlayState creates.
    """

    def __init__(self, app):
        super().__init__(app)
        self.title_font = pygame.font.SysFont(None, 64)
        self.label_font = pygame.font.SysFont(None, 28)
        self.option_font = pygame.font.SysFont(None, 30)
        self.prompt_font = pygame.font.SysFont(None, 24)

        self.selected_num_players = settings.DEFAULT_NUM_PLAYERS

        self.title_y = settings.SCREEN_HEIGHT // 3
        self.label_y = settings.SCREEN_HEIGHT // 2 - 50
        self.options_y = settings.SCREEN_HEIGHT // 2 - 10
        self.start_y = settings.SCREEN_HEIGHT // 2 + 80

        self.option_buttons = self._layout_option_buttons()
        self.start_button = pygame.Rect(0, 0, 200, 44)
        self.start_button.center = (settings.SCREEN_WIDTH // 2, self.start_y)

    def _layout_option_buttons(self):
        button_size = 56
        gap = 20
        total_width = (
            len(PLAYER_COUNT_OPTIONS) * button_size
            + (len(PLAYER_COUNT_OPTIONS) - 1) * gap
        )
        start_x = (settings.SCREEN_WIDTH - total_width) // 2

        buttons = {}
        for i, count in enumerate(PLAYER_COUNT_OPTIONS):
            x = start_x + i * (button_size + gap)
            buttons[count] = pygame.Rect(x, self.options_y, button_size, button_size)
        return buttons

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.app.quit()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._start_game()
                elif event.unicode.isdigit() and int(event.unicode) in self.option_buttons:
                    self.selected_num_players = int(event.unicode)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for count, rect in self.option_buttons.items():
                    if rect.collidepoint(event.pos):
                        self.selected_num_players = count
                if self.start_button.collidepoint(event.pos):
                    self._start_game()

    def _start_game(self):
        from game.states.play_state import PlayState
        self.app.change_state(PlayState(self.app, num_players=self.selected_num_players))

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(settings.BLACK)

        title_surf = self.title_font.render(settings.TITLE, True, settings.WHITE)
        title_rect = title_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, self.title_y))
        screen.blit(title_surf, title_rect)

        label_surf = self.label_font.render("Select number of players", True, settings.WHITE)
        label_rect = label_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, self.label_y))
        screen.blit(label_surf, label_rect)

        for count, rect in self.option_buttons.items():
            is_selected = count == self.selected_num_players
            color = settings.BUTTON_HOVER_COLOR if is_selected else settings.BUTTON_COLOR
            pygame.draw.rect(screen, color, rect, border_radius=8)
            num_surf = self.option_font.render(str(count), True, settings.WHITE)
            num_rect = num_surf.get_rect(center=rect.center)
            screen.blit(num_surf, num_rect)

        pygame.draw.rect(screen, settings.BUTTON_COLOR, self.start_button, border_radius=6)
        start_surf = self.option_font.render("Start Game", True, settings.WHITE)
        start_rect = start_surf.get_rect(center=self.start_button.center)
        screen.blit(start_surf, start_rect)

        prompt_surf = self.prompt_font.render(
            "Click a number, then Start Game  \u2014  ESC to quit", True, settings.GRAY
        )
        prompt_rect = prompt_surf.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 24)
        )
        screen.blit(prompt_surf, prompt_rect)
