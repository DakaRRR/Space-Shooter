import pygame
import os
import random

pygame.font.init()
width, height = 1000, 1000
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space war")

# -----Загрузка изображений для игры-----

# Космо-корабль
space_ship = pygame.image.load(os.path.join("images", "space-ship.png"))
red_space_ship = pygame.image.load(os.path.join("images", "space-ship-red.png"))
blue_space_ship = pygame.image.load(os.path.join("images", "space-ship-blue.png"))

# Лазеры
def_laser = pygame.image.load(os.path.join("images", "laser.png"))
red_laser = pygame.image.load(os.path.join("images", "laser-red.png"))
blue_laser = pygame.image.load(os.path.join("images", "laser-blue.png"))

# Фон
bg = pygame.transform.scale(pygame.image.load(os.path.join("images", "space.png")),
                            (width, height))  # Сопоставляю размер с окном игры
#
university = pygame.transform.scale(pygame.image.load(os.path.join("images", "kazguu.png")), (700,250))


# ---- Лазер ----
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

# --- Корабль ----
class Ship:
    cd = 30 # перезарядка


    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    # Отображение корабля и лазеров
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    # Движение лазеров
    def move_lasers(self, vel, obj):
        self.cooldown() # Проверка перезарядки
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10  # Если попал по кораблю игрока отнимает 10 здоровья
                self.lasers.remove(laser) # Удаление лазера

    # Перезарядка
    def cooldown(self):
        if self.cool_down_counter >= self.cd:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    # Выстрел
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+125, self.y+20, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    # Данные ширины
    def get_width(self):
        return self.ship_img.get_width()

    # Данные высоты
    def get_height(self):
        return self.ship_img.get_height()


#---- Игрок -----
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)  # данные корабля
        self.ship_img = space_ship
        self.laser_img = def_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)


    # Отображение полосы со здоровьем над кораблем (зеленая и красная)
    def health_bar(self,window):
        # зеленая - цвет, координаты от точка а до точки б, ширина полоски
        pygame.draw.rect(window, (255, 0, 0),(self.x+25, self.y + self.ship_img.get_height() - 50, self.ship_img.get_width()-60, 5))
        # красная - так же + меняет свой цвет в зависимости от количества текущего здоровья
        pygame.draw.rect(window, (0, 255, 0), (self.x+25, self.y + self.ship_img.get_height() - 50, (self.ship_img.get_width() * (self.health / self.max_health)) -60,5))


# --- Противник -----
class Enemy(Ship):
    # разные корабли и разные лазеры врагов
    color_map = {
                "red": (red_space_ship, red_laser),
                "blue": (blue_space_ship, blue_laser)
                }

    #отображение корабля нужного цвета
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.color_map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+75, self.y+115, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

# при попадении выстрела на корабль исчезает
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


# ------Запуск игры ------
def main():
    run = True
    FPS = 90
    lvl = 0
    lives = 3

    main_font = pygame.font.SysFont("arial", 75)  # Параметры текста
    lost_font = pygame.font.SysFont("arial", 100)  # Параметры текста проигрыша

    enemies = []

    enemy_vel = 1  # Количество пикселей движения вражеского корабля

    wave_length = 5  # Продолжительность волн

    lost = False  # Проигрыш
    lost_count = 0

    player_vel = 10  # Количество пикселей движения корабля

    laser_vel = 5

    player = Player(375, 775)  # Координаты расположения корабля

    clock = pygame.time.Clock()

    # Установка фона
    def redraw_window():
        win.blit(bg, (0, 0))
        # Вставка текста
        lives_label = main_font.render(f"Жизни: {lives}", 1, (255, 255, 255))
        lvl_label = main_font.render(f"Уровень: {lvl}", 1, (255, 255, 255))

        win.blit(lives_label, (10, 10))  # Жизни слева сверху
        win.blit(lvl_label, (width - lvl_label.get_width() - 10, 10))  # Уровень сверху справа

        # Рисуем корабли врагов
        for enemy in enemies:
            enemy.draw(win)

        # Корабль игрока
        player.draw(win)

        # Если игра проиграна
        if lost:
            lost_label = lost_font.render("Вы проиграли!", 1, (255, 255, 255))
            win.blit(lost_label, (width / 2 - lost_label.get_width() / 2, 450))

        pygame.display.update()

    while run:
        clock.tick(FPS)  # для 90 FPS
        redraw_window()

        # Проверка кол-ва жизней и здоровья
        if lives <= 0 or player.health <= 0:
            lost = True  # Игра проиграна
            lost_count += 1

        # Завершение игры при проигрыше
        if lost:
            if lost_count > FPS * 2:  # Задержка перед закрытием
                run = False
            else:
                continue

        if len(enemies) == 0:  # если врагов не осталось уровень пройден
            lvl += 1
            wave_length += 5
            for i in range(wave_length):  # Генерация врагов
                # рандомное расположение спавна врагов и их цвет
                enemy = Enemy(random.randrange(100, width - 100), random.randrange(-1750, -150),
                              random.choice(["red", "blue"]))
                enemies.append(enemy)

        # Выход
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        # Установка значения клавиш
        keys = pygame.key.get_pressed()
        if keys[
            pygame.K_a] and player.x - player_vel > 0:  # если клавиша Ф и не перелетает границы и корабль, то движение влево
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < width:  # Направо
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # Вверх
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < height:  # Вниз
            player.y += player_vel
        if keys[pygame.K_SPACE]:  # на пробеле - стрелять
            player.shoot()

        # Движение врагов и проверка
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 40) == 1: # первые выстрелы противника
                enemy.shoot()


            if collide(enemy, player):
                player.health -= 10 # если попадает по игру минус 10 хп
                enemies.remove(enemy) # удалние корабля при попадении игроков

            # если противник дойдет до низа, минус жизнь и его удаление
            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)

        # направление выстрела корабля( минус чтобы стрелял с верхней его точки)
        player.move_lasers(-laser_vel, enemies)

#Меню
def game_menu():
    # Параметры текста вступления
    intro_font = pygame.font.SysFont("comicsans",60)
    run=True
    # Запуск цикла
    while run:
        win.blit(bg,(0,0)) # Отображение фона
        win.blit(university, (width/2 - university.get_width()/2, 100))
        # Текст
        intro_text = intro_font.render("Нажмите на кнопку мыши чтобы начать",1,(255,255,255))
        # Расположение по центру
        win.blit(intro_text,(width/2 - intro_text.get_width()/2,450))

        pygame.display.update()

        # Если нажат крестик, завершить игру
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # Кнопка мыши -> запуск игры
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit() #выход

game_menu() #запуск
