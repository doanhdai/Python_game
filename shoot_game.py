import pygame
from pygame import mixer
import os
import random
import csv
import button
# Khởi tạo mixer cho âm thanh
mixer.init()
# Khởi tạo tất cả các module Pygame
pygame.init()

# Đặt chiều rộng màn hình
SCREEN_WIDTH = 800
# Đặt chiều cao màn hình bằng 80% chiều rộng
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

# Tạo cửa sổ game với kích thước đã định
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# Đặt tiêu đề cho cửa sổ game
pygame.display.set_caption('bắn súng mario game')

# Tạo đối tượng Clock để kiểm soát framerate
clock = pygame.time.Clock()
# Đặt số khung hình trên giây (FPS)
FPS = 60

# Định nghĩa các biến game
GRAVITY = 0.75  # Hệ số trọng lực
SCROLL_THRESH = 200  # Ngưỡng cuộn màn hình
ROWS = 16  # Số hàng trong lưới game
COLS = 150  # Số cột trong lưới game
TILE_SIZE = SCREEN_HEIGHT // ROWS  # Kích thước mỗi ô trong lưới
TILE_TYPES = 21  # Số loại ô (tile) khác nhau
MAX_LEVELS = 2  # Số level tối đa

screen_scroll = 0  # Biến theo dõi cuộn màn hình
bg_scroll = 0  # Biến theo dõi cuộn nền
def save_progress(level):
    with open('progress.txt', 'w') as file:
        file.write(str(level))

def load_progress():
    if os.path.exists('progress.txt'):
        with open('progress.txt', 'r') as file:
            return int(file.read())
    return 1  # Nếu chưa có file lưu, bắt đầu từ level 1
level = load_progress()  # Level hiện tại
start_game = False  # Trạng thái bắt đầu game
start_intro = False  # Trạng thái bắt đầu intro

player_damage = 1  # Sát thương người chơi chịu
ai_damage = 50  # Sát thương AI (kẻ địch) chịu

#define player action variables

moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.05)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.05)


#load images
#button images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
#background
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/Tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)
#bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
#grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
#pick up boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
pause_img = pygame.image.load('img/pause.png').convert_alpha()
pause_img = pygame.transform.scale(pause_img, (80, 80))
level_img = pygame.image.load('img/level.png').convert_alpha()
level_img = pygame.transform.scale(level_img, (200,200))
win_img = pygame.image.load('img/win.png')
win_img = pygame.transform.scale(win_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
continue_img = pygame.image.load('img/pause.png').convert_alpha()
continue_img = pygame.transform.scale(continue_img, (100, 100))

lv1 = pygame.image.load('img/lv1.png')
lv1 = pygame.transform.scale(lv1, (100, 100))

lv2 = pygame.image.load('img/lv2.png')
lv2 = pygame.transform.scale(lv2, (100, 100))

item_boxes = {
	'Health'	: health_box_img,
	'Ammo'		: ammo_box_img,
	'Grenade'	: grenade_box_img
}


#màu sắc mặc định
BG = (255, 255, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

#font chữ mặc định
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


def draw_bg():
	screen.fill(BG)
	width = sky_img.get_width()
	for x in range(5):
		screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
		screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
		screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
		screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


#function to reset level
def reset_level():
	enemy_group.empty()
	bullet_group.empty()
	grenade_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	#create empty tile list
	data = []
	for row in range(ROWS):
		r = [-1] * COLS
		data.append(r)
  
	return data


class Soldier(pygame.sprite.Sprite):
    
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        # Khởi tạo các thuộc tính cơ bản của nhân vật
        self.alive = True
        self.char_type = char_type  # Loại nhân vật (player hoặc enemy)
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1  # 1 là phải, -1 là trái
        self.vel_y = 0  # Vận tốc theo trục y
        self.jump = False
        self.in_air = True
        self.flip = False  # Đảo ngược hình ảnh
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # 0: đứng yên, 1: chạy, 2: nhảy, 3: chết
        self.update_time = pygame.time.get_ticks()

        # Các biến đặc biệt cho AI
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)  # Tầm nhìn của AI
        self.idling = False
        self.idling_counter = 0
        
        # Tải tất cả hình ảnh cho nhân vật
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # Cập nhật thời gian hồi chiêu bắn
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # Reset các biến di chuyển
        screen_scroll = 0
        dx = 0
        dy = 0

        # Xác định hướng di chuyển
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Nhảy
        if self.jump == True and self.in_air == False:
            self.vel_y = -15
            self.jump = False
            self.in_air = True

        # Áp dụng trọng lực
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Kiểm tra va chạm với các obstacle
        for tile in world.obstacle_list:
            # Kiểm tra va chạm theo trục x
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # Nếu là AI và đụng tường, đổi hướng
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # Kiểm tra va chạm theo trục y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Kiểm tra nếu đang nhảy
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # Kiểm tra nếu đang rơi
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # Kiểm tra va chạm với nước
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # Kiểm tra va chạm với cửa ra
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # Kiểm tra nếu rơi khỏi map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # Kiểm tra nếu đi ra khỏi cạnh màn hình
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # Cập nhật vị trí nhân vật
        self.rect.x += dx
        self.rect.y += dy

        # Cập nhật scroll dựa trên vị trí người chơi
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.5 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            # Giảm đạn
            self.ammo -= 1
            shot_fx.play()
            


    def ai(self):
        if self.alive and player.alive:
            # Xác suất AI đứng yên
            if self.idling == False and random.randint(1, 100) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50
            # Kiểm tra nếu AI gần người chơi
            if self.vision.colliderect(player.rect):
                # Dừng và đối mặt với người chơi
                self.update_action(0)  # 0: idle
                # Bắn
                self.shoot()
            else:
                if self.idling == False:
					# if (self.direction == 1 and player.rect.centerx < self.rect.centerx) or (self.direction == -1 and player.rect.centerx > self.rect.centerx):
					# 		# Nếu người chơi ở phía ngược lại, AI lật lại
					# 	self.direction *= -1
                    
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1

                    # Cập nhật tầm nhìn AI khi di chuyển
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    #hiển thị khung hình của máymáy
                    # pygame.draw.rect(screen, (255, 0, 0), self.vision, 2)
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # Scroll
        self.rect.x += screen_scroll 

    def update_animation(self):
        # Cập nhật animation
        ANIMATION_COOLDOWN = 100
        # Cập nhật hình ảnh dựa trên frame hiện tại
        self.image = self.animation_list[self.action][self.frame_index]
        # Kiểm tra nếu đủ thời gian đã trôi qua kể từ lần cập nhật cuối
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # Nếu animation đã kết thúc thì reset về đầu
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # Kiểm tra nếu hành động mới khác hành động trước đó
        if new_action != self.action:
            self.action = new_action
            # Cập nhật các thiết lập animation
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        
        
class World():
    def __init__(self):
        self.obstacle_list = []  # Danh sách chứa các obstacle trong thế giới game
    def adjust_difficulty(self, level):
        """Điều chỉnh độ khó của game."""
        if level == 2:
            self.player_damage = 20  # Tăng sát thương kẻ địch
            self.ai_damage = 20
        else:
            self.enemy_speed = 2
            self.enemy_damage = 50
    def process_data(self, data):
        self.level_length = len(data[0])  # Độ dài của level
        # Duyệt qua từng giá trị trong file dữ liệu level
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]  # Lấy hình ảnh tương ứng với loại tile
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)  # Thêm obstacle vào danh sách
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)  # Tạo đối tượng nước
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)  # Tạo đối tượng trang trí
                        decoration_group.add(decoration)
                    elif tile == 15:  # Tạo người chơi
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 2, 7, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:  # Tạo kẻ địch
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 2, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:  # Tạo hộp đạn
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:  # Tạo hộp lựu đạn
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:  # Tạo hộp máu
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:  # Tạo cửa ra
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return player, health_bar  # Trả về người chơi và thanh máu

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll  # Cập nhật vị trí x của obstacle theo screen scroll
            screen.blit(tile[0], tile[1])  # Vẽ obstacle lên màn hình
            
            
            
            
class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


	def update(self):
		#scroll
		self.rect.x += screen_scroll
		#check if the player has picked up the box
		if pygame.sprite.collide_rect(self, player):
			#check what kind of box it was
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 15
			elif self.item_type == 'Grenade':
				player.grenades += 3
			#delete the item box
			self.kill()


class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		#update with new health
		self.health = health
		#calculate health ratio
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#move bullet
		self.rect.x += (self.direction * self.speed) + screen_scroll
		#check if bullet has gone off screen
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()
		#check for collision with level
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		#check collision with characters
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= player_damage
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= ai_damage
					self.kill()



class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction

	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

		#check for collision with level
		for tile in world.obstacle_list:
			#check collision with walls
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			#check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				#check if below the ground, i.e. thrown up
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom	


		#update grenade position
		self.rect.x += dx + screen_scroll
		self.rect.y += dy

		#countdown timer
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			grenade_fx.play()
			explosion = Explosion(self.rect.x, self.rect.y, 0.5)
			explosion_group.add(explosion)
			#do damage to anyone that is nearby
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health -= 50



class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0


	def update(self):
		#scroll
		self.rect.x += screen_scroll

		EXPLOSION_SPEED = 4
		#update explosion amimation
		self.counter += 1

		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			#if the animation is complete then delete the explosion
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]


class ScreenFade():
	def __init__(self, direction, colour, speed):
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0


	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:#whole screen fade
			pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
			pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
		if self.direction == 2:#vertical screen fade down
			pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
		if self.fade_counter >= SCREEN_WIDTH:
			fade_complete = True

		return fade_complete


#create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)


#create buttons
# Khởi tạo các nút bấm để chọn level
start_btn = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 - 100, start_img, 1)  # Level 1 button
level1_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 - 200, lv1, 1)  # Level 2 button
level2_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 - 100, lv2, 1)
select_level = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 - 30, level_img, 1)
# start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 140, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)
pause_button = button.Button(SCREEN_WIDTH - 110, 10, pause_img, 1)
continue_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, continue_img, 1)



#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



#create empty tile list
def load_level_data(level):
    """Load the world data from a CSV file for the given level."""
    world_data = []
    with open(f'level{level}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            r = [int(tile) for tile in row]  # Convert each tile to an integer
            world_data.append(r)
    return world_data
   
   
world = World()
# player, health_bar = world.process_data(world_data)
paused = False  # Trạng thái tạm dừng
game_won = False
quite_home = True
open_menu_level = False
run = True
while run:

	clock.tick(FPS)

	if start_game == False:
		#draw menu
		screen.fill(BG)
		#add buttons
		if not paused:
			if quite_home:
				if start_btn.draw(screen):
					# level = 1 
					start_game = True
					# start_intro = True
					player, health_bar = world.process_data(load_level_data(level))
				# if level2_button.draw(screen):
				if select_level.draw(screen):
					# pause_button.draw(screen)
					open_menu_level = True
					quite_home = False
					exit_button.draw(screen)
			else:
				if exit_button.draw(screen):
					run = False
				elif open_menu_level:

					if level1_button.draw(screen):
						if open_menu_level == True:
							open_menu_level = False
							level = 1
							start_game = True
							player, health_bar = world.process_data(load_level_data(level))
					if level2_button.draw(screen):
						if open_menu_level == True:
							
							quite_home = True     
		if exit_button.draw(screen):  # Exit button inside level menu
			run = False
	elif paused:
        # Hiển thị menu Pause
		screen.fill(BG)
		# draw_text('Game Paused', font, WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 200)

		if continue_button.draw(screen):  # Tiếp tục trò chơi
			paused = False
		if exit_button.draw(screen):  # Thoát
			run = False
	elif game_won:
		screen.blit(win_img, (0, 0))
		if exit_button.draw(screen):
			run = False
	else:
		
		#update background
		draw_bg()
		#draw world map
		world.draw()
		#show player health
		health_bar.draw(player.health)
		#show ammo
		draw_text('AMMO: ', font, WHITE, 10, 35)
		for x in range(player.ammo):
			screen.blit(bullet_img, (90 + (x * 10), 40))
		#show grenades
		draw_text('GRENADES: ', font, WHITE, 10, 60)
		for x in range(player.grenades):
			screen.blit(grenade_img, (135 + (x * 15), 60))


		player.update()
		player.draw()

		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()

		#update and draw groups
		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		bullet_group.draw(screen)
		grenade_group.draw(screen)
		explosion_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)

  
  
		if pause_button.draw(screen):
			paused =True
			# start_game = False
			
		#show intro
		if start_intro == True:
			if intro_fade.fade():
				start_intro = False
				intro_fade.fade_counter = 0


		#update player actions
		if player.alive:
			#shoot bullets
			if shoot:
				player.shoot()
			#throw grenades
			elif grenade and grenade_thrown == False and player.grenades > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
				 			player.rect.top, player.direction)
				grenade_group.add(grenade)
				#reduce grenades
				player.grenades -= 1
				grenade_thrown = True
			if player.in_air:
				player.update_action(2)#2: jump
			elif moving_left or moving_right:
				player.update_action(1)#1: run
			else:
				player.update_action(0)#0: idle
			screen_scroll, level_complete = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
			#check if player has completed the level
			if level_complete:
				# start_intro = True
				
				level += 1
				bg_scroll = 0
				if level > MAX_LEVELS:
        # Người chơi đã vượt qua tất cả các level
					game_won = True

					# start_game = False
				else:
					save_progress(level)
					world_data = reset_level()
					if level <= MAX_LEVELS:
						#load in level data and create world
						with open(f'level{level}_data.csv', newline='') as csvfile:
							reader = csv.reader(csvfile, delimiter=',')
							for x, row in enumerate(reader):
								for y, tile in enumerate(row):
									world_data[x][y] = int(tile)
						world = World()
						player, health_bar = world.process_data(world_data)	
		
		else:
			screen_scroll = 0
			if death_fade.fade():
				if restart_button.draw(screen):
					death_fade.fade_counter = 0
					# start_intro = True
					bg_scroll = 0
					world_data = reset_level()
					#load in level data and create world
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)


	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#keyboard presses
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE or event.key == pygame.K_k:
				shoot = True
			if event.key == pygame.K_q:
				grenade = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
				jump_fx.play()
			if event.key == pygame.K_ESCAPE:
				run = False


		#keyboard button released
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE or event.key == pygame.K_k:
				shoot = False
			if event.key == pygame.K_q:
				grenade = False
				grenade_thrown = False


	pygame.display.update()

pygame.quit()