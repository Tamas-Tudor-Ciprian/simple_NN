#these are the dependencies at the heart of the project
import pygame
import gymnasium




class Player:
	def __init__(self, screen):
		self.pos = pygame.Vector2(screen.get_width() /2 , screen.get_height() / 2)






def main():
	pygame.init()
	screen = pygame.display.set_mode((1280, 720))
	clock = pygame.time.Clock()
	running = True
	dt = 0

	player = Player(screen)



	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False



		screen.fill("yellow")

		pygame.draw.circle(screen,"red",player.pos, 40)


		keys = pygame.key.get_pressed()

		if keys[pygame.K_w]:
			player.pos.y -= 300 * dt

		#this is where you are supposed to render the game


		#this puts the work on the screen or smt

		pygame.display.flip()


		dt = clock.tick(60) / 1000 # this limits FPS to 60


	pygame.quit()


if __name__ == "__main__":
	main()
