#these are the dependencies at the heart of the project
import pygame
import gymnasium
import random
from collections import deque




class Player:
	def __init__(self, screen):
		self.pos = pygame.Vector2(screen.get_width() /2 , screen.get_height() / 2)


class Obstacles:
	def __init__(self, screen):
		#here we init the side rects
		self.leftSide = pygame.Rect(screen.get_width() / 2 - 400, 0, 100, 1000)
		self.rightSide = pygame.Rect(screen.get_width() / 2 + 300, 0, 100, 1000)

		#I create and store rectangles in a fifo way
		#they get deleted once they go off screen in the downwards direction
		#they are spawned with random coords between the side rects
		self.obsts = deque()
		self.spawn_timer = 0
		self.spawn_interval = 0.8  # seconds between spawns
		self.speed = 300  # pixels per second

		# playable bounds (inside the side walls)
		self.min_x = self.leftSide.right
		self.max_x = self.rightSide.left

	def manage(self, screen, dt):
		# spawn new obstacles on a timer
		self.spawn_timer += dt
		if self.spawn_timer >= self.spawn_interval:
			self.spawn_timer = 0
			width = random.randint(30, 80)
			height = random.randint(20, 40)
			x = random.randint(self.min_x, self.max_x - width)
			self.obsts.append(pygame.Rect(x, -height, width, height))

		# move all obstacles down
		for obs in self.obsts:
			obs.y += self.speed * dt

		# remove obstacles that have gone off the bottom
		while self.obsts and self.obsts[0].y > screen.get_height():
			self.obsts.popleft()


def check_collision(player, rects, radius=40):
	for rect in rects:
		closest_x = max(rect.left, min(player.pos.x, rect.right))
		closest_y = max(rect.top, min(player.pos.y, rect.bottom))
		dist = player.pos.distance_to(pygame.Vector2(closest_x, closest_y))
		if dist <= radius:
			return True
	return False


def main():
	pygame.init()
	screen = pygame.display.set_mode((1280, 720))
	clock = pygame.time.Clock()
	running = True
	dt = 0

	player = Player(screen)

	obstacles = Obstacles(screen)


	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		# update obstacles
		obstacles.manage(screen, dt)

		# collect all collidable rects (walls + falling blocks)
		all_rects = [obstacles.leftSide, obstacles.rightSide] + list(obstacles.obsts)

		# check for death
		if check_collision(player, all_rects):
			print("Game Over!")
			running = False

		# move player
		keys = pygame.key.get_pressed()
		if keys[pygame.K_a]:
			player.pos.x -= 300 * dt
		if keys[pygame.K_d]:
			player.pos.x += 300 * dt

		# draw everything
		screen.fill("yellow")
		pygame.draw.circle(screen, "red", player.pos, 40)
		for rect in all_rects:
			pygame.draw.rect(screen, "blue", rect)

		pygame.display.flip()

		dt = clock.tick(60) / 1000 # this limits FPS to 60


	pygame.quit()


if __name__ == "__main__":
	main()
