# import pygame package
import pygame


# initializing imported module
pygame.init()
WHITE = (255, 255, 255)
BLACK = (0,0,0)

screen = pygame.display.set_mode((640, 360))
screen.fill(WHITE)
Clock = pygame.time.Clock()
pygame.display.flip()

# creating a bool value which checks
# if game is running
running = True
prev = (320, 180)
# keep game running till running is true
while running:
    Pos = pygame.mouse.get_pos()
    # Check for event if user has pushed
    # any event in queue
    for event in pygame.event.get():
        if event.type == pygame.mouse.get_pressed(3):
            if event[1]:
                pygame.draw.line(screen, BLACK, prev, Pos, )
                prev = Pos
                Pos = pygame.mouse.get_pos()


        # if event is of type quit then
        # set running bool to false
        if event.type == pygame.QUIT:
            running = False

    prev = Pos