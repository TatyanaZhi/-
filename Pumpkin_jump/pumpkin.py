#Импортируем Pygame
import pygame
import random

#Инициализируем 
pygame.init()

#Параметры экрана
WIN_WIDTH = 640
WIN_HEIGHT = 960

clock = pygame.time.Clock()
FPS = 60

#Гравитация
GRAVITY = 1

# Максимальное количество островов на экране
MAX_ISLAND = 10


#Цвета игры
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (245, 61, 61)
GREEN = (0, 142, 74)
ORANGE = (248, 144, 17)


#Размер игрового окна
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption('PumpkinCat') #Название игры, отображается сверху в панельке

#Загрузка фона
pum_image = pygame.image.load('gmImg/pumpkin.png').convert_alpha() #герой
bg_image = pygame.image.load('gmImg/bg.png').convert_alpha() #фон
island_image = pygame.image.load('gmImg/isl.png').convert_alpha() #остовки

#класс игрока
class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pum_image, (80, 80)) #Масштаировали игрока
        self.width = 40
        self.height = 70
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0 #Переменная перемещения по Y
        self.flip = False #Переменная, которая будет поворачивать игрока
        
    #Движение игрока
    def move(self):
        dx = 0
        dy = 0
    #Клавиши управления героем
        key = pygame.key.get_pressed() #Функция нажатия клавиши
        if key[pygame.K_a]:
            dx = -10
            self.flip = False
        if key[pygame.K_d]:
            dx = 10
            self.flip = True

        #Гравитация
        self.vel_y += GRAVITY #Движение вниз (падение)
        dy += self.vel_y

        #Проверка что игрок не выходит за край экрана
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > WIN_WIDTH:
            dx = WIN_WIDTH - self.rect.right

        #Сталкивание с платформами
        for island in island_group:
            #направление сталкиваний
            if island.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #столкновение о поверхность острова
                if self.rect.bottom < island.rect.centery:
                    if self.vel_y > 0:
                     self.rect.bottom = island.rect.top
                     dy = 0 # Касается острова
                     self.vel_y = -20 #Подпрыгивает

        
        #Проверка что игрок отталкивается от пола    
        if self.rect.bottom + dy > WIN_HEIGHT:
            dy = 0 # Касается земли
            self.vel_y = -20 #Подпрыгивает

        #обновление позиции
        self.rect.x += dx
        self.rect.y += dy

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -12, self.rect.y -5))
        pygame.draw.rect(screen, WHITE, self.rect, 1)

#Класс островков
class Island(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(island_image, (110, 50)) #уменьшаю длину острова
        self.rect = self.image.get_rect() #задаю размер прямоугольника острова
        self.rect.x = x
        self.rect.y = y

pumpkin = Player(WIN_WIDTH // 2, WIN_HEIGHT - 150)       

#Создаю группы спрайтов островов
island_group = pygame.sprite.Group()

#Временные платформы для проверки
for p in range(MAX_ISLAND):
    p_w = random.randint(40, 60)
    p_x = random.randint(0, WIN_WIDTH - p_w)
    p_y = p * random.randint(80, 120)
    island = Island(p_x, p_y, p_w) 
    island_group.add(island) #будет добавлять нов.острова

#Цикл чтобы окно не закрывалось
w_run = True
while w_run:

    clock.tick(FPS)
    pumpkin.move()

    #Чтобы отобразилось фотоное изображение
    screen.blit(bg_image, (0, 0)) #координаты расположения фонового изображения
    
    #отрисовака островов
    island_group.draw(screen)
    #отрисовка игрока
    pumpkin.draw()

    #Событие нажатие на крестик
    for event in pygame.event.get():  #Обработчик событий
        if event.type == pygame.QUIT:
            w_run = False

    #чтобы экран обновлялся
    pygame.display.update()

pygame.quit()