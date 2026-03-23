#these are the dependencies at the heart of the project
import pygame
import gymnasium
from collections import deque




class Player:
	def __init__(self, screen):
		self.pos = pygame.Vector2(screen.get_width() /2 , screen.get_height() / 2)


class Obstacles:
	def __init__(self,screen):
		#here we init the side rects

		self.leftSide = pygame.Rect(screen.get_width() /2 - 400, 0,100,1000)

		self.rightSide = pygame.Rect(screen.get_width() / 2 + 300 , 0 , 100, 1000)
	
	def manage(self,screen):
		#I create and store rectangles in a fifo way
		#they get deleted once they go off screen in the downwards direction
		#they are spawned with random coords between the side rects
		obsts = deque()

		if obsts.len() < 1:
			pass


def main():
	pygame.init()
	screen = pygame.display.set_mode((1280, 720))
	clock = pygame.time.Clock()
	running = True
	dt = 0

	player = Player(screen)

	obstacles = Obstacles(screen)


	rects = [obstacles.leftSide, obstacles.rightSide]


	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False


		

		screen.fill("yellow")

		pygame.draw.circle(screen,"red",player.pos, 40)

		for rect in rects:
			pygame.draw.rect(screen, "blue", rect)



		keys = pygame.key.get_pressed()

		if keys[pygame.K_a]:
			player.pos.x -= 300 * dt
		if keys[pygame.K_d]:
			player.pos.x += 300 * dt

		#this is where you are supposed to render the game


		#this puts the work on the screen or smt

		pygame.display.flip()


		dt = clock.tick(60) / 1000 # this limits FPS to 60


	pygame.quit()


if __name__ == "__main__":
	main()
