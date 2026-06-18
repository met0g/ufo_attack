import pygame
import sys
import config
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PATH, SOUND_PATH, WHITE, GREEN, RED, BOSS_TRIGGER_SCORE, DEV_MODE_ENABLED
from sprites import Cannon, Bullet, UFO, Town, Home, UFOBoss, UFOBossSummon, BossLaser
from menu import StartMenu

# Инициализация Pygame и аудио-микшера
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Защита города от НЛО")
clock = pygame.time.Clock()

# --- Загрузка фоновых спрайтов ---
try:
    background_image = pygame.image.load(f"{PATH}background.png").convert()
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    ground_image = pygame.image.load(f"{PATH}graund.png").convert_alpha()
    ground_image = pygame.transform.scale(ground_image, (SCREEN_WIDTH, 40))
except pygame.error as e:
    print(f"Ошибка загрузки фоновых спрайтов: {e}")
    pygame.quit()
    sys.exit()

# --- Загрузка звуков и музыки ---
try:
    pygame.mixer.music.load(f"{SOUND_PATH}bcm.wav")
    shot_sound = pygame.mixer.Sound(f"{SOUND_PATH}sh.wav")
    boom_sound = pygame.mixer.Sound(f"{SOUND_PATH}boom.wav")

    shot_sound.set_volume(0.6)
    boom_sound.set_volume(0.7)
    pygame.mixer.music.set_volume(0.5)
except pygame.error as e:
    print(f"Ошибка загрузки аудиофайлов: {e}")
    pygame.quit()
    sys.exit()


def main():
    # --- Запуск стартового меню ---
    menu = StartMenu(screen)
    menu.run()

    # --- Инициализация объектов геймплея ---
    cannon = Cannon()
    bullets = []
    ufos = []
    buildings = []

    # Объекты Босса
    boss = None
    summons = []
    laser = None

    town_positions = [60, 160, 580, 680]
    home_positions = [110, 220, 320, 520, 740]

    for x in town_positions:
        buildings.append(Town(x))
    for x in home_positions:
        buildings.append(Home(x))

    score = 0
    font = pygame.font.SysFont("Arial", 24)

    # Включаем зацикленную фоновую музыку
    pygame.mixer.music.play(-1)

    SPAWN_UFO_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_UFO_EVENT, 1300)

    # Таймер появления приспешников босса (каждые 2.5 секунды)
    SPAWN_SUMMON_EVENT = pygame.USEREVENT + 2
    boss_events_started = False

    running = True
    boss_phase = False

    while running:
        dt = clock.tick(FPS)

        # 1. События
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == SPAWN_UFO_EVENT and not boss_phase:
                ufos.append(UFO())

            if event.type == SPAWN_SUMMON_EVENT and boss_phase and boss:
                summons.append(UFOBossSummon(boss.x, boss.y + 40))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                bullets.append(Bullet(cannon.x, cannon.y, cannon.angle))
                cannon.shoot()
                shot_sound.play()

                # --- ИНСТРУМЕНТЫ РАЗРАБОТЧИКА (DEV ФУНКЦИИ) ---
            if event.type == pygame.KEYDOWN:
                    # Все эти клавиши сработают ТОЛЬКО если в настройках включена галочка!
                if config.DEV_MODE_ENABLED:

                        # Клавиша S: Спавн одного обычного НЛО
                    if event.key == pygame.K_s:
                        if not boss_phase:
                            ufos.append(UFO())
                            print("Dev: Заспавнено 1 НЛО")

                        # Клавиша B: Мгновенный вызов Босса
                    if event.key == pygame.K_b:
                        if not boss_phase:
                            boss_phase = True
                            boss = UFOBoss()
                            ufos.clear()
                            print("Dev: Вызван Босс!")

                        # Клавиша K: Уничтожить всех врагов на экране
                        if event.key == pygame.K_k:
                            ufos.clear()
                            summons.clear()
                            if boss:
                                boss = None
                                boss_phase = False
                                print("Dev: Босс уничтожен кнопкой!")
                            else:
                                print("Dev: Все обычные враги зачищены!")

        # Автоматическая активация фазы босса по достижении нужного счета
        if score >= BOSS_TRIGGER_SCORE and not boss_phase:
            boss_phase = True
            boss = UFOBoss()
            ufos.clear()

        if boss_phase and not boss_events_started:
            pygame.time.set_timer(SPAWN_SUMMON_EVENT, 2500)
            boss_events_started = True

        # 2. Обновление позиций и логики объектов
        cannon.update(dt)

        for b in buildings:
            b.animate(dt)

        for bullet in bullets[:]:
            bullet.update()
            if bullet.y < 0 or bullet.x < 0 or bullet.x > SCREEN_WIDTH:
                bullets.remove(bullet)

        # Логика обычных НЛО (до фазы босса)
        if not boss_phase:
            for ufo in ufos[:]:
                ufo.update()
                ufo_rect = pygame.Rect(ufo.x - ufo.width // 2, ufo.y - ufo.height // 2, ufo.width, ufo.height)

                for b in buildings:
                    if ufo_rect.colliderect(b.rect) and b.hp > 0:
                        b.take_damage()
                        boom_sound.play()
                        if ufo in ufos: ufos.remove(ufo)
                        break

                if ufo.y > SCREEN_HEIGHT:
                    if ufo in ufos: ufos.remove(ufo)

        # Логика Босса (во время фазы босса)
        else:
            if boss:
                boss.update(dt)

                # Зарядка и выстрел луча (8 секунд)
                if boss.laser_timer >= boss.laser_charge_time and not boss.is_firing_laser:
                    boss.is_firing_laser = True
                    boss.laser_timer = 0
                    laser = BossLaser(boss.x, boss.y + 50)
                    boom_sound.play()

                # Если луч горит и прожигает здания
                if boss.is_firing_laser and laser:
                    laser.update(dt, boss.x)

                    for b in buildings:
                        if b.hp > 0 and laser.rect.colliderect(b.rect):
                            b.take_damage(2)  # Плавный урон прожиганием

                    # Луч исчезает через 1 секунду работы
                    if laser.timer >= laser.life_time:
                        boss.is_firing_laser = False
                        laser = None

                # Обновление приспешников-камикадзе
                target_bullet = bullets[0] if bullets else None
                for s in summons[:]:
                    s.update(dt, target_bullet)
                    if s.y > SCREEN_HEIGHT:
                        summons.remove(s)

        # Проверка поражения (если все здания разрушены)
        alive_buildings = sum(1 for b in buildings if b.hp > 0)
        if alive_buildings == 0:
            print(f"Город разрушен! Игра окончена. Твой счет: {score}")
            running = False

        # 3. Расчет коллизий снарядов игрока
        for bullet in bullets[:]:
            hit_something = False

            # Коллизия с обычными НЛО
            if not boss_phase:
                for ufo in ufos[:]:
                    ufo_rect = pygame.Rect(ufo.x - ufo.width // 2, ufo.y - ufo.height // 2, ufo.width, ufo.height)
                    if bullet.rect.colliderect(ufo_rect):
                        ufos.remove(ufo)
                        score += 1
                        hit_something = True
                        break

            # Коллизии в битве с Боссом
            else:
                # Приспешники перехватывают снаряды
                for s in summons[:]:
                    if bullet.rect.colliderect(s.rect):
                        summons.remove(s)
                        hit_something = True
                        break

                # Если снаряд не попал в приспешника, наносим урон боссу
                if not hit_something and boss and bullet.rect.colliderect(boss.rect):
                    boss.hp -= 1
                    hit_something = True
                    if boss.hp <= 0:
                        score += 50  # Бонусные очки
                        print(f"ПОБЕДА! Босс повержен! Финальный счет: {score}")
                        boss = None
                        summons.clear()
                        boss_phase = False  # Возвращаемся в обычный бесконечный режим

            if hit_something and bullet in bullets:
                bullets.remove(bullet)

        # 4. Отрисовка графики по слоям
        screen.blit(background_image, (0, 0))
        screen.blit(ground_image, (0, SCREEN_HEIGHT - 40))

        for b in buildings:
            b.draw(screen)

        for bullet in bullets:
            bullet.draw(screen)

        cannon.draw(screen)

        if not boss_phase:
            for ufo in ufos:
                ufo.draw(screen)
        else:
            if laser:
                laser.draw(screen)
            for s in summons:
                s.draw(screen)
            if boss:
                boss.draw(screen)

                # Индикатор здоровья босса
                hp_bar_width = 120
                hp_bar_height = 8
                hp_bar_x = boss.x - hp_bar_width // 2
                hp_bar_y = boss.y - 60
                pygame.draw.rect(screen, RED, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
                pygame.draw.rect(screen, GREEN, (hp_bar_x, hp_bar_y, int(hp_bar_width * (boss.hp / 4)), hp_bar_height))

        # Вывод текста интерфейса
        score_text = font.render(f"Счет: {score}", True, WHITE)
        buildings_text = font.render(f"Зданий уцелело: {alive_buildings}/9", True,
                                     GREEN if alive_buildings > 3 else RED)
        screen.blit(score_text, (10, 10))
        screen.blit(buildings_text, (SCREEN_WIDTH - 240, 10))

        pygame.display.flip()

    # Завершение работы программы
    pygame.mixer.music.fadeout(500)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()