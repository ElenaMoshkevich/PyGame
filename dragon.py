import os
from random import randrange, choice
import csv
import pygame
import pygame_menu

DIRECTION = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
SIZE = 20
WIDTH = 600  # высота окна
LENGTH = 600  # ширина окна
FPS = 5


def start_game():  # создает стартовое меню
    screen_size = (LENGTH, WIDTH + 200)
    screen = pygame.display.set_mode(screen_size)
    fullname = os.path.join('img', 'menu.jpg')
    fon = os.path.join('img', 'instruction.jpg')
    mytheme = pygame_menu.themes.THEME_DARK.copy()
    myimage = pygame_menu.baseimage.BaseImage(
        image_path=fullname,
        drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY)
    mytheme.background_color = myimage
    fonimage = pygame_menu.baseimage.BaseImage(
        image_path=fon,
        drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY)

    def main_background() -> None:
        fonimage.draw(screen)

    menu = pygame_menu.Menu(height=300, width=410, title='Поехали?',
                            theme=mytheme, position=(50, 95))
    menu.add.button('Play', run)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    menu.mainloop(screen, main_background)


def load_image(name):
    # получение всех поворотов из картинки
    fullname = os.path.join('img', name)
    image = {}
    try:
        img = pygame.image.load(fullname)
        colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image["up"] = img
    image["right"] = pygame.transform.rotate(img, -90)
    image["down"] = pygame.transform.rotate(img, 180)
    image["left"] = pygame.transform.rotate(img, 90)
    return image


def read_levels(file_name):
    # загрузим примеры их файла csv, получим список словарей
    # в словаре заданы: логическая операция(как в питоне), аргументы и верный ответ
    levels = []
    fullname = os.path.join('data', file_name)
    try:
        with open(fullname, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in list(reader)[1:]:
                level = {}
                level["op"] = row[0]
                level["arg1"] = row[1]
                level["arg2"] = row[2]
                level["answer"] = row[3]
                levels.append(level)
    except pygame.error as message:
        print('Не удаётся загрузить:', file_name)
        raise SystemExit(message)

    return levels


def screen_level(screen, level):
    # На копии экрана отрисовываем новое задание
    fullname = os.path.join('img', 'fon_level.jpg')
    screen2 = pygame.Surface(screen.get_size())
    # screen2.fill(COLORFON)
    img = pygame.image.load(fullname).convert()
    screen2.blit(img, (0, 0))
    arg_a = level["arg1"]
    arg_b = level["arg2"]
    op = level["op"]
    font = pygame.font.Font(None, 50)
    task1 = font.render(f" A     B    A {op} B ", 3, (0, 165, 0))
    task2 = font.render(f" {arg_a}      {arg_b}         ? ", 1, (0, 165, 0))
    task_x = LENGTH // 2 - task1.get_width() // 2 + 20
    task_y = WIDTH + 55
    task_w = task1.get_width()
    task_h = task1.get_height()
    screen2.blit(task1, (task_x, task_y))
    screen2.blit(task2, (task_x, task_y + 50))
    pygame.draw.rect(screen2, (255, 45, 0), (5, 5, LENGTH - 10, WIDTH - 10), 5)
    pygame.draw.rect(screen2, (0, 45, 0), (task_x - 10, task_y - 10,
                                           task_w + 7, task_h + 70), 3)
    pygame.draw.rect(screen2, (100, 45, 0), (5, WIDTH + 5, LENGTH - 10, 190), 5)
    pygame.draw.line(screen2, (0, 45, 0), (task_x - 10, task_y + 40),
                     (task_x - 10 + task_w + 7, task_y + 40), 3)
    pygame.draw.rect(screen2, (0, 45, 0), (task_x + 50, task_y - 10,
                                           task_w // 3 - 10, task_h + 70), 3)

    return screen2


def close_game(screen, results):
    font_end = pygame.font.SysFont('Arial', 50, bold=True)
    font_message = pygame.font.SysFont('Arial', 20, bold=True)
    if results < 2:
        screen.fill((255, 0, 0))
        render_end = font_end.render('GAME OVER', 1, pygame.Color('white'))
        screen.blit(render_end, (LENGTH // 2 - 100, WIDTH // 2))
        render_message = font_message.render(f'Вы проиграли, "Дракон" разрушился :((', 1, pygame.Color('white'))
        screen.blit(render_message, (LENGTH // 2 - 170, 95))
    elif results == 12:
        screen.fill((0, 155, 0))
        render_end = font_end.render('Mission Complete!!!', 1, pygame.Color('white'))
        screen.blit(render_end, (LENGTH // 2 - 200, WIDTH // 3))
        render_message = font_message.render(f'"Дракон" возвращается на базу c полной загрузкой :))',
                                             1, pygame.Color('white'))
        screen.blit(render_message, (25, 15))
    else:
        screen.fill((0, 0, 155))
        render_end = font_end.render('Mission completed partially!!!', 1, pygame.Color('white'))
        screen.blit(render_end, (20, WIDTH // 3))
        render_message = font_message.render(f'"Дракон" возвращается на базу c {results} контейнерами :))', 1,
                                             pygame.Color('white'))
        screen.blit(render_message, (15, 15))

    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 50
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, choice(numbers), choice(numbers))


class Particle(pygame.sprite.Sprite):
    # для имитации взрыва топлива создадим различные частицы
    fire = []
    img = load_image("st.png")
    for scale in (5, 10, 20):
        for dir in ("up", "down", "left", "right"):
            im = pygame.transform.scale(img[dir], (scale, scale))
            fire.append(im)

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = choice(self.fire)
        self.rect = self.image.get_rect()
        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx * 10, dy * 10]
        # и свои координаты
        self.rect.x, self.rect.y = pos

    def update(self):
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        screen_rect = (0, 0, LENGTH, WIDTH)
        if not self.rect.colliderect(screen_rect):
            self.kill()

    def kill_all(self):
        screen_rect = (0, 0, 1, 1)
        if not self.rect.colliderect(screen_rect):
            self.kill()



class Snake:
    # создание змейки
    def __init__(self, x=WIDTH // 2, y=LENGTH // 2, direction="up"):
        # значения по умолчанию
        self.x = x  # начальное положение
        self.y = y
        self.direction = direction  # направление движения
        self.list_snake = [(self.x, self.y, self.direction), (self.x, self.y - SIZE, self.direction)]
        self.set_image()  # загрузка всех рисунков и их различных поворотов
        self.set_sound()
        self.food_coord = self.food()  # получаем словарь с координатами целей
        self.correct_food = "0"

    def set_image(self):
        self.head_image = load_image('head.bmp')  # голова
        self.body_image = load_image('body.bmp')  # тело
        self.tail_image = load_image('tail.bmp')  # хвост
        self.zero_image = load_image('zero.png')["up"]  # астероид с нулем
        self.unit_image = load_image('unit.png')["up"]  # астероид с единицей

    def set_sound(self):
        try:
            self.sound_ok = pygame.mixer.Sound("data/ok.mp3")
            self.sound_not_ok = pygame.mixer.Sound("data/not_ok.mp3")
            self.sound_cross = pygame.mixer.Sound("data/cross.mp3")
        except pygame.error as message:
            print('Не удаётся загрузить звук')
            raise SystemExit(message)

    def render(self, screen):  # отрисовка всех частей змейки и астероидов
        screen.blit(self.head_image[self.list_snake[-1][2]], (self.list_snake[-1][0], self.list_snake[-1][1], 20, 20))
        for i in range(1, len(self.list_snake) - 1):
            screen.blit(self.body_image[self.list_snake[i][2]], (self.list_snake[i][0], self.list_snake[i][1], 20, 20))
        screen.blit(self.tail_image[self.list_snake[1][2]], (self.list_snake[0][0], self.list_snake[0][1], 20, 20))
        screen.blit(self.zero_image, (*self.food_coord["0"], 20, 20))
        screen.blit(self.unit_image, (*self.food_coord["1"], 20, 20))

    def crossing(self):  # определение"самопересечения" змейки
        list_coord = [(i[0], i[1]) for i in self.list_snake]
        return len(list_coord) != len(set(list_coord))

    def move(self):  # Добавление нового первого элемента и удаление последнего
        dx, dy = DIRECTION[self.direction]
        x, y = self.list_snake[-1][0], self.list_snake[-1][1]
        self.list_snake.pop(0)
        self.list_snake.append(((x + SIZE * dx) % LENGTH, (y + SIZE * dy) % WIDTH, self.direction))

    def expel(self):  # удаление одного элемента с хвоста
        self.list_snake.pop(0)

    def supplement(self):  # добавление элемента впереди по направлению движения
        dx, dy = DIRECTION[self.direction]
        x, y = self.list_snake[-1][0], self.list_snake[-1][1]
        self.list_snake.append(((x + SIZE * dx) % LENGTH, (y + SIZE * dy) % WIDTH, self.direction))

    def food(self):  # создаем 2 цели 0 и 1
        x0, y0 = randrange(SIZE, LENGTH - SIZE, SIZE), randrange(SIZE, WIDTH - SIZE, SIZE)
        x1, y1 = randrange(SIZE, LENGTH - SIZE, SIZE), randrange(SIZE, WIDTH - SIZE, SIZE)
        list_coord = [(i[0], i[1]) for i in self.list_snake]
        while (x0, y0) in list_coord:
            x0, y0 = randrange(SIZE, LENGTH - SIZE, SIZE), randrange(SIZE, WIDTH - SIZE, SIZE)
        while (x1, y1) in list_coord:
            x1, y1 = randrange(SIZE, LENGTH - SIZE, SIZE), randrange(SIZE, WIDTH - SIZE, SIZE)
        return {"0": (x0, y0), "1": (x1, y1)}

    def eat_food(self):  # определяем захвачен ли астероид(еда)
        if (self.list_snake[-1][0], self.list_snake[-1][1]) == self.food_coord[self.correct_food]:
            # если захвачена верная цель
            self.supplement()  # добавляем сегмент
            self.food_coord = self.food()  # генерируем новые цели
            return True, True
        if (self.list_snake[-1][0], self.list_snake[-1][1]) == self.food_coord[
            self.not_correct_food(self.correct_food)]:
            self.expel()
            self.food_coord = self.food()
            return True, False
        return False, False

    def not_correct_food(self, food):  # получаем противоположный правильноу ответ
        if food == "0":
            return "1"
        return "0"

    def update(self):
        food, rez = self.eat_food()
        if self.crossing():
            for i in range(len(self.list_snake) - 1):
                create_particles((self.list_snake[i][0], self.list_snake[i][1]))
            self.expel()
            self.sound_cross.play()
            return False
        if food:
            if rez:
                self.sound_ok.play()
            else:
                create_particles((self.list_snake[-1][0], self.list_snake[-1][1]))
                self.sound_not_ok.play()
            return True
        return False


def run():
    screen_size = (LENGTH, WIDTH + 200)
    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()
    running = True
    levels = read_levels("levels.csv")  # загружаем все задания
    level = randrange(0, len(levels))  # случайно выбираем задание
    data = levels.pop(level)  # удаляем задание из списка, сохраняем данные
    sc = screen_level(screen, data)  # получаем экран с заданием
    font_score = pygame.font.SysFont('Arial', 26, bold=True)
    sn = Snake()
    sn.correct_food = data["answer"]
    while running:  # запускаем игровой цикл
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:  # отслеживаем нажатие стрелок,
                # следим чтобы не было нажато противоположное движению направление
                if event.key == pygame.K_LEFT and sn.direction != "right":
                    sn.direction = "left"
                    break
                if event.key == pygame.K_RIGHT and sn.direction != "left":
                    sn.direction = "right"
                    break
                if event.key == pygame.K_UP and sn.direction != "down":
                    sn.direction = "up"
                    break
                if event.key == pygame.K_DOWN and sn.direction != "up":
                    sn.direction = "down"
                    break
        pygame.display.flip()
        screen.blit(sc, (0, 0))
        all_sprites.draw(screen)
        all_sprites.update()
        if sn.update():  # проверяем захватила ли змейка астероид, обрабатываем результат захвата
            # если захват произошёл, получаем новое задание
            level = randrange(0, len(levels))
            data = levels.pop(level)
            sc = screen_level(screen, data)
            sn.correct_food = data["answer"]
        if len(sn.list_snake) < 2 or len(levels) == 0 or len(sn.list_snake) >= 12:
            # проверяем все случаи завершения игры
            close_game(screen, len(sn.list_snake))
            return
            # running = False
        else:
            sn.render(screen)
            sn.move()
            clock.tick(FPS)
            render_score = font_score.render(f'SCORE: {len(sn.list_snake) - 2}', 1, pygame.Color('orange'))
            screen.blit(render_score, (15, WIDTH + 25))


def main():
    pygame.init()
    pygame.display.set_caption('Приручи "Дракона"')
    while True:
        start_game()
    pygame.quit()


if __name__ == '__main__':
    all_sprites = pygame.sprite.Group()
    main()
