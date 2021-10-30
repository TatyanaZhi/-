#Импортируем Pygame
import pygame
import random
import os
from pygame import mixer

#Инициализируем 
mixer.init()
pygame.init()

#Параметры экрана
WIN_WIDTH = 640
WIN_HEIGHT = 960


clock = pygame.time.Clock()
FPS = 60

#Загрузка музыки
pygame.mixer.music.load('gmImg/kif.mp3')
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1, 0.0)
jump_fx = pygame.mixer.Sound('gmImg/prig.mp3')
jump_fx.set_volume(0.6)
death_fx = pygame.mixer.Sound('gmImg/death.mp3')
death_fx.set_volume(0.5)

#Линия-разделитель прокрутки
SCROLL_LINE = 200
scroll = 0 #Переменная для прокрутки 
bg_scroll = 0 #Переменная для прокрутки фона
game_over = False #Переменная для окончания игры
score = 0 #Переменая посчета очков
fade_counter = 0 #переменная затухания

if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        hight_score = int(file.read())
else:
    hight_score = 0

#Гравитация
GRAVITY = 1

# Максимальное количество островов на экране
MAX_ISLAND = 10


#Цвета игры
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 142, 74)
ORANGE = (248, 144, 17)
PANEL = (8, 0, 38)

#Шрифты
font_small = pygame.font.SysFont('Arial Black', 20)
font_big = pygame.font.SysFont('Arial Black', 36)
font_big_big = pygame.font.SysFont('Arial Black', 40)

#Размер игрового окна
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption('PumpkinCat') #Название игры, отображается сверху в панельке

#Загрузка фона
pum_image = pygame.image.load('gmImg/pumpkin.png').convert_alpha() #герой
bg_image = pygame.image.load('gmImg/bg.png').convert_alpha() #фон
island_image = pygame.image.load('gmImg/isl.png').convert_alpha() #остовки
gov_image = pygame.image.load('gmImg/gov.png').convert_alpha() 

#Функция написания текста на экране
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#Функция написания счета на экране
def draw_panel():
    pygame.draw.rect(screen, PANEL, (0, 0, WIN_WIDTH, 30))
    pygame.draw.line(screen, ORANGE, (0, 30), (WIN_WIDTH, 30), 2)
    draw_text('СЧЕТ: ' + str(score), font_small, ORANGE, 0, 0) 

#функция для рисования непрерывного фона
def draw_bg(bg_scroll):
    screen.blit(bg_image, (0, 0 + bg_scroll))
    screen.blit(bg_image, (0, -960 + bg_scroll))

#def draw_gov():
    #screen.blit(gov_image, (0, 0, WIN_WIDTH))


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
        scroll = 0
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

        #Сталкивание с островами
        for island in island_group:
            #направление сталкиваний
            if island.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #столкновение о поверхность острова
                if self.rect.bottom < island.rect.centery:
                    if self.vel_y > 0:
                     self.rect.bottom = island.rect.top
                     dy = 0 # Касается острова
                     self.vel_y = -20 #Подпрыгивает
                     jump_fx.play()
        
        #Проверка отскачил ли игрок в верхнюю часть экрана (для прокрутки)
        if self.rect.top <= SCROLL_LINE:
            if self.vel_y < 0:  #чтобы фон не прокручивался обратно
                scroll = -dy

        
        #Проверка что игрок отталкивается от пола    
        #if self.rect.bottom + dy > WIN_HEIGHT:
            #dy = 0 # Касается земли
            #self.vel_y = -25 #Подпрыгивает

        #обновление позиции
        self.rect.x += dx
        self.rect.y += dy + scroll

        return scroll #добавляем возврат прокрутки

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x -12, self.rect.y -5))
        #pygame.draw.rect(screen, WHITE, self.rect, 1)

#Класс островков
class Island(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(island_image, (130, 60)) #уменьшаю длину острова
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)# Рандомная скорость для движущихся платфор
        self.rect = self.image.get_rect() #задаю размер прямоугольника острова
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        #Движущие острова 
        if self.moving == True:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed

        #Смена направления платормы
        if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > WIN_WIDTH:
            self.direction *= -1
            self.move_counter = 0

        #обновление островов
        self.rect.y += scroll

        #проверка чтобы остава не выходли за границу экрана 
        if self.rect.top > WIN_HEIGHT:
            self.kill()

        #Чтобы не выходил остров за край справа (двигать обратно)
        if self.rect.right > WIN_WIDTH:
            self.rect.x -= 5
            
            

pumpkin = Player(WIN_WIDTH // 2, WIN_HEIGHT - 150)       

#Создаю группы спрайтов островов
island_group = pygame.sprite.Group()

#Временные острова для проверки
#for p in range(MAX_ISLAND):
     #p_w = random.randint(40, 60)
     #p_x = random.randint(0, WIN_WIDTH - p_w)
     #p_y = p * random.randint(80, 120)
    #island = Island(p_x, p_y, p_w) 
    #island_group.add(island) #будет добавлять нов.острова
#Острова
island = Island(WIN_WIDTH // 2 - 50, WIN_HEIGHT - 50, 100, False) #начальный остров
island_group.add(island)


#Цикл чтобы окно не закрывалось
w_run = True
while w_run:

    clock.tick(FPS)

    if game_over == False:
        scroll = pumpkin.move()

        #чтобы отобразилось фотоное изображение
        bg_scroll += scroll
        if bg_scroll >= 960:
            bg_scroll = 0
        draw_bg(bg_scroll)
        
        #отрисовка линии прокрутки
        #pygame.draw.line(screen, ORANGE,(0, SCROLL_LINE), (WIN_WIDTH, SCROLL_LINE))

        #Генератор островов
        if len(island_group) < MAX_ISLAND:
            p_w = random.randint(40, 60)
            p_x = random.randint(0, WIN_WIDTH - p_w)
            p_y = island.rect.y - random.randint(80, 120)
            p_type = random.randint(1, 2) #Переменая для движущего острова
            if p_type == 1 and score > 500:
                p_moving = True
            else:
                p_moving = False
            island = Island(p_x, p_y, p_w, p_moving)
            island_group.add(island)


        #обновление островов
        island_group.update(scroll)

        #обновление счета
        if scroll > 0:
            score += scroll
        #Линия самого большого счета
        pygame.draw.line(screen, ORANGE, (0, score - hight_score + SCROLL_LINE), (WIN_WIDTH, score - hight_score + SCROLL_LINE), 3)
        draw_text('ПРЕДЫДУЩИЙ РЕКОРД', font_small, ORANGE, SCROLL_LINE - 130, score - hight_score + SCROLL_LINE)

        #отрисовака островов
        island_group.draw(screen)
        #отрисовка игрока
        pumpkin.draw()

        #отображение счета
        draw_panel()

        #конец игры (если кот упал)
        if pumpkin.rect.top > WIN_HEIGHT:
            game_over = True
            death_fx.play()
            
    else:
        if fade_counter < WIN_WIDTH:
            fade_counter += 20
            pygame.draw.rect(screen, BLACK, (0, 0, fade_counter, WIN_HEIGHT))
        else:
            draw_text('КОНЕЦ ИГРЫ', font_big_big, WHITE, WIN_WIDTH // 2 - 150, 300)        
            draw_text('ОЧКИ: ' + str(score), font_big, WHITE, WIN_WIDTH // 3, 500)
            draw_text('НАЖМИ ПРОБЕЛ, ЧТОБЫ НАЧАТЬ СНОВА', font_small, GREEN, 70, 700)
            
   

            #Обновление самого большого счета и запись в файл
            if score > hight_score:
                hight_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(hight_score))

            key = pygame.key.get_pressed() #Кнопка начатьс с начала
            if key[pygame.K_SPACE]:
                game_over = False
                score = 0
                scroll = 0
                fade_counter = 0
                #Появление игрока после нажатия SPACE
                pumpkin.rect.center = (WIN_WIDTH // 2, WIN_HEIGHT - 150)
                #Появление первого острова после перезагрузки
                island_group.empty()
                #Острова
                island = Island(WIN_WIDTH // 2 - 50, WIN_HEIGHT - 50, 100, False) #начальный остров
                island_group.add(island)

    #Событие нажатие на крестик
    for event in pygame.event.get():  #Обработчик событий
        if event.type == pygame.QUIT:
            #Обновление самого большого счета и запись в файл
            if score > hight_score:
                hight_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(hight_score))
            w_run = False

    #чтобы экран обновлялся
    pygame.display.update()

pygame.quit()