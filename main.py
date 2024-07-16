import time
import pygame
import sys
from client import Client
from board import Board
import threading
from consts import *


def drawButton(screen, x, y, text):
    btn = pygame.Rect(x - BUTTON_WIDTH//2, y - BUTTON_HEIGHT //
                      2, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, COLOR_OPTIONS[5], btn, border_radius=5)
    font = pygame.font.SysFont("comicsans", 50)
    message = font.render(text, 1, COLOR_OPTIONS[4])
    message_position = message.get_rect(center=btn.center)
    screen.blit(message, message_position)
    return btn


def homeScreen():
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
    global stopWaiting
    while not stopWaiting.is_set():
        message = client.receive()
        if message and message == "start":
            print("Opponent has been found")
            stopWaiting.set()
        time.sleep(1)


def findingOpponent():
    global stopWaiting
    player = Client()
    playerNum = player.getPlayerNumber()
    print(f"Player {playerNum} connected to server")

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

    board = Board(player, playerNum, screen)
    val = board.startGame()
    endGame(val)


def endGame(reason):
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
homeScreen()

"""
  TASKS
  - tie
  - have check/checkmate account for en passant and castling
  - handle opponent disconnecting when game starts
"""
