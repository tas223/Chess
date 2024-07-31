import time
import pygame
import sys
from client import Client
from board import Board
import threading
from consts import *


def drawButton(screen, x, y, text):
    """Draws a button centered at (x,y) with text displaying over it

    Args:
        screen (pygame.Surface): The pygame surface that the user interacts with
        x (int): The x-coordinate for the button's center
        y (int): The y-coordinate for the button's center
        text (str): The message to display in the buttom

    Returns:
        pygame.Rect: The button's rectangle object, which is used to detect button clicks
    """
    btn = pygame.Rect(x - BUTTON_WIDTH//2, y - BUTTON_HEIGHT //
                      2, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, COLOR_OPTIONS[5], btn, border_radius=5)
    font = pygame.font.SysFont("comicsans", 50)
    message = font.render(text, 1, COLOR_OPTIONS[4])
    message_position = message.get_rect(center=btn.center)
    screen.blit(message, message_position)
    return btn


def homeScreen():
    """
        Displays a home screen, where a user can choose to join a new game and be directed to the next screen.
    """
    while True:
        screen.fill(COLOR_OPTIONS[4])

        joinGame = drawButton(screen, WIDTH//2, HEIGHT//2, "Join a Game")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if joinGame.collidepoint(pos):
                    findingOpponent()
                    return

        pygame.display.update()


def waitingForOpponent(client):
    """ Runs in a loop until opponent is found or user exits.

    Args:
        client (Client): client object to communicate with the game server.
    """
    global stopWaiting, playerNumber

    while not stopWaiting.is_set():
        message = client.receive()
        if message and (message == "0" or message == "1"):
            print("Opponent has been found")
            playerNumber = int(message)
            stopWaiting.set()
        time.sleep(1)


def unableToConnect():
    """
        If server is at occupancy limit or client fails to connect, notify user of error.
    """
    screen.fill(COLOR_OPTIONS[5])
    drawButton(screen, 400, 400, "Can't Connect to Server")
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def findingOpponent():
    """
        Handles connection to the server, waiting for opponent, and start/end of game.
        Uses threading when waiting for opponent to prevent lags in display.
        The stopWaiting threading event is needed for a user to exit without waitingForOpponent preventing pygame from exiting.
    """
    global stopWaiting, playerNumber
    player = Client()
    successfulConnection = player.validConnection()

    if not successfulConnection:
        player.close()
        unableToConnect()
        return

    print(f"Player connected to server")
    screen.fill(COLOR_OPTIONS[5])
    drawButton(screen, 400, 400, "Looking for Opponent")
    pygame.display.update()

    stopWaiting.clear()
    waitingThread = threading.Thread(target=waitingForOpponent, args=(player,))
    waitingThread.start()

    while not stopWaiting.is_set():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stopWaiting.set()
                player.close()
                pygame.quit()
                sys.exit()

    board = Board(player, playerNumber, screen)
    val = board.startGame()
    endGame(val)


def endGame(reason):
    """Displays a screen with the reason why the game ended.

    Args:
        reason (int): The reason the game ended
    """

    message = ["Your Opponent Disconnected.",
               "Congrats! You Won!", "Checkmate. You Lose."]
    screen.fill(COLOR_OPTIONS[5])
    drawButton(screen, 400, 400, message[reason])
    pygame.display.update()
    time.sleep(3)
    homeScreen()


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
stopWaiting = threading.Event()
playerNumber = 0
homeScreen()
