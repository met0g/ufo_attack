import pygame
import random
import math
import sys
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PATH, BLUE, WHITE,
    TOWN_MAX_DEPTH, TOWN_MAX_HEIGHT, HOME_MAX_DEPTH, HOME_MAX_HEIGHT, BOSS_MAX_HP
)


class Town(pygame.sprite.Sprite):
    """Класс большой высотки (100 HP, высота 100 пикселей)."""

    def __init__(self, x):
        super().__init__()
        self.hp = 100
        self.x = x
        self.offset_y = random.randint(-TOWN_MAX_HEIGHT, TOWN_MAX_DEPTH)
        self.y = (SCREEN_HEIGHT - 40 - 100) + self.offset_y

        try:
            self.sprites = {
                100: [pygame.image.load(f"{PATH}town 20x100.png").convert_alpha()],
                70: [
                    pygame.image.load(f"{PATH}town 20x100(70 xp 1).png").convert_alpha(),
                    pygame.image.load(f"{PATH}town 20x100(70 xp 2).png").convert_alpha(),
                    pygame.image.load(f"{PATH}town 20x100(70 xp 3).png").convert_alpha()
                ],
                40: [
                    pygame.image.load(f"{PATH}town 20x100(40 xp 1).png").convert_alpha(),
                    pygame.image.load(f"{PATH}town 20x100(40 xp 2).png").convert_alpha(),
                    pygame.image.load(f"{PATH}town 20x100(40 xp 3).png").convert_alpha()
                ],
                10: [
                    pygame.image.load(f"{PATH}town 20x100(10 xp 1).png").convert_alpha(),
                    pygame.image.load(f"{PATH}town 20x100(10 xp 2).png").convert_alpha(),
                    pygame.image.load(f"{PATH}town 20x100(10 xp 3).png").convert_alpha()
                ],
                0: [pygame.image.load(f"{PATH}town 20x100(dead).png").convert_alpha()]
            }
        except pygame.error as e:
            print(f"Ошибка загрузки спрайтов Town: {e}")
            pygame.quit()
            sys.exit()

        self.current_stage = 100
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 250

        self.image = self.sprites[self.current_stage][self.current_frame]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def take_damage(self, amount=30):
        if self.hp > 0:
            self.hp -= amount
            if self.hp < 0: self.hp = 0

            old_stage = self.current_stage
            if self.hp > 70:
                self.current_stage = 100
            elif self.hp > 40:
                self.current_stage = 70
            elif self.hp > 10:
                self.current_stage = 40
            elif self.hp > 0:
                self.current_stage = 10
            else:
                self.current_stage = 0

            if old_stage != self.current_stage:
                self.current_frame = 0

    def animate(self, dt):
        frames = self.sprites[self.current_stage]
        if len(frames) > 1:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(frames)
        else:
            self.current_frame = 0
        self.image = frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Home(pygame.sprite.Sprite):
    """Класс маленького домика (40 HP, высота 20 пикселей)."""

    def __init__(self, x):
        super().__init__()
        self.hp = 40
        self.x = x
        self.offset_y = random.randint(-HOME_MAX_HEIGHT, HOME_MAX_DEPTH)
        self.y = (SCREEN_HEIGHT - 40 - 20) + self.offset_y

        try:
            self.sprites = {
                40: [pygame.image.load(f"{PATH}home 20x20.png").convert_alpha()],
                10: [
                    pygame.image.load(f"{PATH}home 20x20(10 xp 1).png").convert_alpha(),
                    pygame.image.load(f"{PATH}home 20x20(10 xp 2).png").convert_alpha(),
                    pygame.image.load(f"{PATH}home 20x20(10 xp 3).png").convert_alpha()
                ],
                0: [pygame.image.load(f"{PATH}home 20x20(dead).png").convert_alpha()]
            }
        except pygame.error as e:
            print(f"Ошибка загрузки спрайтов Home: {e}")
            pygame.quit()
            sys.exit()

        self.current_stage = 40
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 250

        self.image = self.sprites[self.current_stage][self.current_frame]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def take_damage(self, amount=15):
        if self.hp > 0:
            self.hp -= amount
            if self.hp < 0: self.hp = 0

            old_stage = self.current_stage
            if self.hp > 10:
                self.current_stage = 40
            elif self.hp > 0:
                self.current_stage = 10
            else:
                self.current_stage = 0

            if old_stage != self.current_stage:
                self.current_frame = 0

    def animate(self, dt):
        frames = self.sprites[self.current_stage]
        if len(frames) > 1:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(frames)
        else:
            self.current_frame = 0
        self.image = frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Cannon:
    """Класс пушки (Танковое основание + анимированное дуло)."""

    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 20

        try:
            self.base_image = pygame.image.load(f"{PATH}tank60x60.png").convert_alpha()
            self.gun_frames = [
                pygame.image.load(f"{PATH}gun.png").convert_alpha(),
                pygame.image.load(f"{PATH}gun(s 1).png").convert_alpha(),
                pygame.image.load(f"{PATH}gun(s 2).png").convert_alpha()
            ]
        except pygame.error as e:
            print(f"Ошибка загрузки спрайтов пушки: {e}")
            pygame.quit()
            sys.exit()

        self.rect = self.base_image.get_rect(center=(self.x, self.y))
        self.angle = 0

        self.current_frame = 0
        self.shot_timer = 0
        self.shot_speed = 80
        self.is_shooting = False

    def shoot(self):
        self.is_shooting = True
        self.current_frame = 1
        self.shot_timer = 0

    def update(self, dt):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.x, mouse_y - self.y
        self.angle = math.degrees(-math.atan2(rel_y, rel_x)) - 90

        if self.is_shooting:
            self.shot_timer += dt
            if self.shot_timer >= self.shot_speed:
                self.shot_timer = 0
                self.current_frame += 1
                if self.current_frame >= len(self.gun_frames):
                    self.current_frame = 0
                    self.is_shooting = False

    def draw(self, surface):
        surface.blit(self.base_image, self.rect)

        current_gun_image = self.gun_frames[self.current_frame]
        rotated_gun = pygame.transform.rotate(current_gun_image, self.angle)
        rotated_rect = rotated_gun.get_rect(center=(self.x, self.y))

        surface.blit(rotated_gun, rotated_rect)


class Bullet:
    """Класс снаряда со загрузкой спрайта bullet 10x10."""

    def __init__(self, x, y, angle_degrees):
        self.x = x
        self.y = y
        self.speed = 12

        try:
            self.image = pygame.image.load(f"{PATH}bullet 10x10.png").convert_alpha()
        except pygame.error as e:
            print(f"Ошибка загрузки спрайта пули: {e}")
            pygame.quit()
            sys.exit()

        angle_rad = math.radians(-angle_degrees - 90)
        self.dx = self.speed * math.cos(angle_rad)
        self.dy = self.speed * math.sin(angle_rad)

        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class UFO:
    """Класс обычного НЛО."""

    def __init__(self):
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = -30
        self.speed = random.uniform(1.5, 3.5)
        self.width = 50
        self.height = 18

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        pygame.draw.ellipse(surface, BLUE,
                            (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height))
        pygame.draw.circle(surface, WHITE, (self.x, self.y - 4), 8)


# ================== КЛАССЫ ДЛЯ БОССА ==================
class UFOBoss(pygame.sprite.Sprite):
    """Класс Главного Босса (200x100, 4 HP). Анимация привязана к зарядке лазера."""

    def __init__(self):
        super().__init__()
        self.hp = BOSS_MAX_HP
        self.width = 200
        self.height = 100

        # Спавнится сверху по центру
        self.x = SCREEN_WIDTH // 2
        self.y = -self.height

        self.speed_y = 1.0  # Скорость захода на экран
        self.speed_x = 2.0  # Скорость движения по горизонтали
        self.direction_x = 1  # Направление вправо/влево
        self.target_y = 80  # Высота, на которой останавливается для боя

        # Загрузка 8 кадров анимации босса
        self.frames = []
        try:
            for i in range(1, 9):
                # Загружаем файлы строго по твоим именам: Ufo_boss(200x100 1_8).png и т.д.
                img = pygame.image.load(f"{PATH}Ufo_boss(200x100 {i}_8).png").convert_alpha()
                self.frames.append(img)
        except pygame.error as e:
            print(f"Ошибка загрузки анимации босса: {e}")
            pygame.quit()
            sys.exit()

        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

        # Таймеры для лазера
        self.laser_charge_time = 8000  # 8 секунд зарядки в миллисекундах
        self.laser_timer = 0
        self.is_firing_laser = False

    def update(self, dt):
        # 1. Логика движения
        if self.y < self.target_y:
            # Босс медленно вылетает сверху экрана
            self.y += self.speed_y
        else:
            # Босс летит горизонтально из стороны в сторону
            self.x += self.speed_x * self.direction_x
            if self.x - self.width // 2 <= 0 or self.x + self.width // 2 >= SCREEN_WIDTH:
                self.direction_x *= -1  # Меняем направление при ударе о край экрана

            # Зарядка лазера происходит только тогда, когда босс занял позицию
            if not self.is_firing_laser:
                self.laser_timer += dt

        # 2. АНИМАЦИЯ, ПРИВЯЗАННАЯ К ЗАРЯДКЕ
        if not self.is_firing_laser:
            # Считаем прогресс от 0.0 до 1.0
            progress = self.laser_timer / self.laser_charge_time
            # Переводим прогресс в индекс кадра (от 0 до 7)
            self.current_frame = int(progress * len(self.frames))
            # Защита от выхода за границы списка, если таймер слегка прыгнет вперед
            if self.current_frame >= len(self.frames):
                self.current_frame = len(self.frames) - 1
        else:
            # Во время самого выстрела лазера босс может оставаться на финальном (самом ярком) 8-м кадре
            self.current_frame = len(self.frames) - 1

        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class UFOBossSummon(pygame.sprite.Sprite):
    """Приспешники-камикадзе (20x30). Летят прямо на пули игрока!"""

    def __init__(self, start_x, start_y):
        super().__init__()
        self.x = start_x
        self.y = start_y
        self.speed = 4.5  # Довольно быстрые, чтобы успеть перехватить снаряд

        try:
            self.frames = [
                pygame.image.load(f"{PATH}Ufo_boss_sumon(20x30 1).png").convert_alpha(),
                pygame.image.load(f"{PATH}Ufo_boss_sumon(20x30 2).png").convert_alpha()
            ]
        except pygame.error as e:
            print(f"Ошибка загрузки спрайтов миньонов: {e}")
            pygame.quit()
            sys.exit()

        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 150

        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self, dt, target_bullet=None):
        # Анимация
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

        # ИИ перехвата: если есть выпущенная пуля, летим прямо к ней!
        if target_bullet:
            target_x, target_y = target_bullet.rect.centerx, target_bullet.rect.centery
            rel_x, rel_y = target_x - self.x, target_y - self.y
            distance = math.hypot(rel_x, rel_y)
            if distance != 0:
                self.x += (rel_x / distance) * self.speed
                self.y += (rel_y / distance) * self.speed
        else:
            # Если пуль на экране нет, просто хаотично или плавно спускаются вниз
            self.y += 1.5

        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class BossLaser(pygame.sprite.Sprite):
    """Смертоносный луч босса (600x50, бьет сверху донизу)."""

    def __init__(self, x, y):
        super().__init__()
        try:
            # Загружаем луч
            self.orig_image = pygame.image.load(f"{PATH}Ufo_boss_light(600x50).png").convert_alpha()
        except pygame.error as e:
            print(f"Ошибка загрузки спрайта луча босса: {e}")
            pygame.quit()
            sys.exit()

        # Поворачиваем картинку на 90 градусов, чтобы луч бил вертикально вниз
        self.image = pygame.transform.rotate(self.orig_image, 90)
        # Масштабируем: ширина луча 50, длина — до самого низа экрана
        self.image = pygame.transform.scale(self.image, (50, SCREEN_HEIGHT))

        self.x = x
        self.y = y
        self.rect = self.image.get_rect(midtop=(int(self.x), int(self.y)))

        self.life_time = 1000  # Время удержания луча (1 секунда активного поражения)
        self.timer = 0

    def update(self, dt, boss_x):
        # Луч следует за боссом по оси X во время выстрела
        self.rect.midtop = (int(boss_x), int(self.y))
        self.timer += dt

    def draw(self, surface):
        surface.blit(self.image, self.rect)