import pygame
import sys
import config  # Импортируем весь конфиг, чтобы изменять переменные внутри него


class StartMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_button = pygame.font.SysFont("Arial", 30)
        self.font_sub = pygame.font.SysFont("Arial", 24)

        # Состояние меню: 'main' (главное) или 'settings' (настройки)
        self.state = 'main'

        # Размеры кнопок
        self.button_width = 280
        self.button_height = 60

        # --- ЗАГРУЗКА СПРАЙТОВ ---
        try:
            # Главное лого игры 500x300
            self.logo_sprite = pygame.image.load(f"{config.PATH}logo500x300.png").convert_alpha()
        except pygame.error as e:
            print(f"Ошибка загрузки logo500x300.png: {e}")
            self.logo_sprite = None

        try:
            # Спрайт шестеренки в настройках 200x100
            self.setting_sprite = pygame.image.load(f"{config.PATH}setting 200x100.png").convert_alpha()
        except pygame.error as e:
            print(f"Предупреждение: Не удалось загрузить setting 200x100.png ({e})")
            self.setting_sprite = None

        # --- ПОЗИЦИОНИРОВАНИЕ ЭЛЕМЕНТОВ ---

        # Позиция для ЛОГО (в самом верху по центру)
        if self.logo_sprite:
            self.logo_rect = self.logo_sprite.get_rect(
                center=(config.SCREEN_WIDTH // 2, 170)
            )

        # Кнопки главного меню (сдвинуты чуть ниже, чтобы лого не перекрывало их)
        self.play_button_rect = pygame.Rect(
            (config.SCREEN_WIDTH // 2) - (self.button_width // 2),
            (config.SCREEN_HEIGHT // 2) + 60,
            self.button_width,
            self.button_height
        )
        self.settings_button_rect = pygame.Rect(
            (config.SCREEN_WIDTH // 2) - (self.button_width // 2),
            self.play_button_rect.bottom + 25,
            self.button_width,
            self.button_height
        )

        # Позиция для спрайта настроек 200x100
        if self.setting_sprite:
            self.sprite_rect = self.setting_sprite.get_rect(
                center=(config.SCREEN_WIDTH // 2, (config.SCREEN_HEIGHT // 2) - 100)
            )

        # Квадратный чекбокс для галочки Dev-функций
        self.checkbox_size = 30
        self.checkbox_rect = pygame.Rect(
            (config.SCREEN_WIDTH // 2) - 200,
            (config.SCREEN_HEIGHT // 2) + 30,
            self.checkbox_size,
            self.checkbox_size
        )

        # Кнопка "Назад" в настройках
        self.back_button_rect = pygame.Rect(
            (config.SCREEN_WIDTH // 2) - (self.button_width // 2),
            config.SCREEN_HEIGHT - 120,
            self.button_width,
            self.button_height
        )

        # Цвета кнопок
        self.button_normal_color = config.GREEN
        self.button_hover_color = (100, 255, 100)
        self.settings_normal_color = (130, 130, 240)
        self.settings_hover_color = (180, 180, 255)
        self.back_normal_color = (200, 100, 100)
        self.back_hover_color = (255, 130, 130)

    def draw_main_menu(self, mouse_pos):
        """Отрисовка главного экрана меню"""
        # 1. Отрисовка спрайта ЛОГО вместо скучного текста
        if self.logo_sprite:
            self.screen.blit(self.logo_sprite, self.logo_rect)

        # 2. Кнопка "НАЧАТЬ ИГРУ"
        play_color = self.button_hover_color if self.play_button_rect.collidepoint(
            mouse_pos) else self.button_normal_color
        pygame.draw.rect(self.screen, play_color, self.play_button_rect, border_radius=10)
        play_text = self.font_button.render("НАЧАТЬ ИГРУ", True, (10, 20, 40))
        play_text_rect = play_text.get_rect(center=self.play_button_rect.center)
        self.screen.blit(play_text, play_text_rect)

        # 3. Кнопка "НАСТРОЙКИ"
        settings_color = self.settings_hover_color if self.settings_button_rect.collidepoint(
            mouse_pos) else self.settings_normal_color
        pygame.draw.rect(self.screen, settings_color, self.settings_button_rect, border_radius=10)
        settings_text = self.font_button.render("НАСТРОЙКИ", True, (10, 20, 40))
        settings_text_rect = settings_text.get_rect(center=self.settings_button_rect.center)
        self.screen.blit(settings_text, settings_text_rect)

    def draw_settings_menu(self, mouse_pos):
        """Отрисовка экрана НАСТРОЕК"""
        # В окне настроек оставляем аккуратный текстовый заголовок
        title_text = self.font_button.render("НАСТРОЙКИ", True, config.WHITE)
        title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 180))
        self.screen.blit(title_text, title_rect)

        # 1. Отрисовка спрайта настроек 200x100
        if self.setting_sprite:
            self.screen.blit(self.setting_sprite, self.sprite_rect)

        # 2. Отрисовка чекбокса (галочки)
        pygame.draw.rect(self.screen, config.WHITE, self.checkbox_rect, 2, border_radius=5)
        if config.DEV_MODE_ENABLED:
            inner_rect = self.checkbox_rect.inflate(-10, -10)
            pygame.draw.rect(self.screen, config.GREEN, inner_rect, border_radius=3)

        # Текст рядом с чекбоксом
        dev_text = self.font_sub.render("Включить Dev-функции (клавиши S, B, K)", True, config.WHITE)
        dev_text_rect = dev_text.get_rect(midleft=(self.checkbox_rect.right + 20, self.checkbox_rect.centery))
        self.screen.blit(dev_text, dev_text_rect)

        # 3. Кнопка "НАЗАД"
        back_color = self.back_hover_color if self.back_button_rect.collidepoint(mouse_pos) else self.back_normal_color
        pygame.draw.rect(self.screen, back_color, self.back_button_rect, border_radius=10)
        back_text = self.font_button.render("НАЗАД", True, (10, 20, 40))
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)

    def draw(self):
        self.screen.fill((10, 20, 40))
        mouse_pos = pygame.mouse.get_pos()

        if self.state == 'main':
            self.draw_main_menu(mouse_pos)
        elif self.state == 'settings':
            self.draw_settings_menu(mouse_pos)

    def run(self):
        """Цикл работы меню."""
        clock = pygame.time.Clock()
        menu_running = True

        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == 'main':
                        if self.play_button_rect.collidepoint(event.pos):
                            menu_running = False
                            return True
                        if self.settings_button_rect.collidepoint(event.pos):
                            self.state = 'settings'

                    elif self.state == 'settings':
                        if self.checkbox_rect.collidepoint(event.pos):
                            config.DEV_MODE_ENABLED = not config.DEV_MODE_ENABLED
                            print(f"Dev режим: {config.DEV_MODE_ENABLED}")

                        if self.back_button_rect.collidepoint(event.pos):
                            self.state = 'main'

            self.draw()
            pygame.display.flip()
            clock.tick(30)