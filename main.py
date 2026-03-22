#these are the dependencies at the heart of the project
import pygame
import gymnasium












def main():
	pygame.init()
	screen = pygame.display.set_mode((1280, 720))
	clock = pygame.time.Clock()
	running = True


	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		screen.fill("purple")

		#this is where you are supposed to render the game


		#this puts the work on the screen or smt

		pygame.display.flip()


		clock.tick(60) # this limits FPS to 60


	pygame.quit()


if __name__ == "__main__":
	main()
