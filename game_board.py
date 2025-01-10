import pygame
import socket
from Line import Line

def start_drawing(host, port):

    # create socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))  # Connect to server

    # initializing imported module
    pygame.init()
    white = (255, 255, 255)
    black = (0,0,0)
    green = (0,204,0)
    red = (255,0,0)
    blue  = (0, 102, 255)
    yellow = (255, 255, 0)
    width = 5

    line = Line((255, 255, 255),(1,0),(0,1), 5)


    screen = pygame.display.set_mode((940, 540))
    screen.fill(white)

    clock = pygame.time.Clock()
    clock.tick(30)

    timer = 90 # set the time for the timer (seconds)
    start_time = pygame.time.get_ticks()
    pygame.display.flip()

    color = black # set the starting color

    # creating a bool value which checks
    # if game is running
    running = True

    drawing = False
    # keep game running till running is true

    # Create socket


    while running:


        elapsed_time = (pygame.time.get_ticks() - start_time)/1000 # calculates the time that has passed (in seconds)

        # Check for event if user has pushed
        # any event in queue
        for event in pygame.event.get():
            # define keybinds
            if event.type == pygame.KEYDOWN:
                if event.key ==pygame.K_1:
                    width = 5

                if event.key == pygame.K_2:
                    width = 10

                if event.key == pygame.K_3:
                    width = 15

                if event.key == pygame.K_4:
                    width = 20

                if event.key == pygame.K_5:
                    width = 25

                if event.key == pygame.K_w:
                    color = white

                if event.key == pygame.K_b:
                    color = black

                if event.key == pygame.K_r:
                    color = red

                if event.key == pygame.K_l:
                    color = blue

                if event.key == pygame.K_g:
                    color = green

                if event.key == pygame.K_y:
                    color = yellow

            # checks if timer is over
            if timer - elapsed_time >= 0:

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Start drawing when the mouse button is pressed
                    if event.button == 1:  # Left mouse button
                        drawing = True
                        last_pos = event.pos
                if event.type == pygame.MOUSEBUTTONUP:
                    # Stop drawing when the mouse button is released
                    if event.button == 1:  # Left mouse button
                        drawing = False
                if event.type == pygame.MOUSEMOTION:
                    # Draw on the screen while the mouse moves and the button is pressed
                    if drawing:
                        current_pos = event.pos
                        pygame.draw.line(screen, color, last_pos, current_pos, width)  # Draw a line
                        line.update(color, last_pos, current_pos, width)
                        message = "line/" + line.stringify()  # convert line to string
                        client_socket.send(message.encode())  # Send line data

                        last_pos = current_pos

            # if event is of type quit then
            # set running bool to false
            if event.type == pygame.QUIT:
                message = 'exit'
                client_socket.send(message.encode())  # Send line data
                client_socket.close()  # Close connection
                running = False

        pygame.display.update()


