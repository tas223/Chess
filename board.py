import pygame
import sys
from pieces import *
import time
import threading
from consts import *


class Board:
    def __init__(self, client, player, screen):
        self.screen = screen
        self.board = [[0]*COLS for _ in range(ROWS)]
        self.movingPiece = None
        self.initialRow = -1
        self.initialCol = -1
        self.currentUser = 0
        self.player = player
        self.client = client
        self.lastMove = []
        self.threadingLock = threading.Lock()
        self.end = threading.Event()
        self.receiveThread = None
        self.message = 0
        self.createBoard()
        self.restartPieces()

    def createBoard(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = COLOR_OPTIONS[0] if (
                    row + col) % 2 == 0 else COLOR_OPTIONS[1]
                square = pygame.Rect(col * SQUARE_SIZE, row *
                                     SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, square)

    def showPieces(self):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece:
                    offset = (SQUARE_SIZE-piece.png().get_width())//2
                    self.screen.blit(
                        piece.png(), (offset + col * SQUARE_SIZE, offset + row * SQUARE_SIZE))

    def restartPieces(self):
        whitePieces = [Rook(1), Knight(1), Bishop(1), Queen(
            1), King(1), Bishop(1), Knight(1), Rook(1)]
        blackPieces = [Rook(0), Knight(0), Bishop(0), Queen(
            0), King(0), Bishop(0), Knight(0), Rook(0)]
        for col in range(COLS):
            self.board[0][col] = whitePieces[col]
            self.board[1][col] = Pawn(1)
            self.board[6][col] = Pawn(0)
            self.board[7][col] = blackPieces[col]

    def showMoves(self):
        if self.movingPiece:
            for row, col in self.movingPiece.findMoves(self.board, self.initialRow, self.initialCol, self.lastMove):
                color = COLOR_OPTIONS[2] if (
                    row + col) % 2 == 0 else COLOR_OPTIONS[3]
                square = pygame.Rect(
                    col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, square)

    def showLastMove(self):
        for row, col in self.lastMove:
            color = COLOR_OPTIONS[6] if (
                row + col) % 2 == 0 else COLOR_OPTIONS[7]
            square = pygame.Rect(
                col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(self.screen, color, square)

    def castle(self, row, col):
        if col < self.initialCol:
            self.board[row][3] = self.board[row][0]
            self.board[row][0] = 0
            self.lastMove.extend([(row, 0), (row, 3)])
        else:
            self.board[row][5] = self.board[row][7]
            self.board[row][7] = 0
            self.lastMove.extend([(row, 7), (row, 5)])

    def myTurn(self):
        return self.player == self.currentUser

    def updateBoard(self, moves):
        if len(moves) < 1:  # because send/receive methods are not blocking
            return
        if len(moves) == 1:  # you won or opponent disconnected
            if moves[0][0] == 0:
                self.message = 1
            self.end.set()
            return

        self.lastMove = moves
        row, col = moves[0]
        newRow, newCol = moves[1]
        self.board[newRow][newCol] = self.board[row][col]

        if (newRow == 0 or newRow == 7) and isinstance(self.board[newRow][newCol], Pawn):
            self.board[newRow][newCol] = Queen(not self.player)
        self.board[row][col] = 0
        if len(moves) == 3:  # en passant
            row, col = moves[2]
            self.board[row][col] = 0
        elif len(moves) == 4:  # castling
            row, col = moves[2]
            newRow, newCol = moves[3]
            self.board[newRow][newCol] = self.board[row][col]
            self.board[row][col] = 0

        if not self.validMoves():  # you lost
            self.message = 2
            self.client.send([(0, 0)])
            self.end.set()

    def checkLastMove(self):
        return self.lastMove

    def handleEnPassant(self):
        enPassantRow = 3 if self.player == 0 else 4
        if isinstance(self.movingPiece, Pawn) and self.initialRow == enPassantRow and len(self.lastMove) == 2:
            initialX, initialY = self.lastMove[0]
            finalX, finalY = self.lastMove[1]
            if isinstance(self.board[finalX][finalY], Pawn) and abs(finalX - initialX) == 2 and finalY == initialY and self.initialRow == finalX and abs(finalY - self.initialCol) == 1:
                self.board[finalX][finalY] = 0
                return (finalX, finalY)

    def handleMove(self, row, col):
        if (row, col) in self.movingPiece.findMoves(self.board, self.initialRow, self.initialCol, self.lastMove):
            self.board[row][col] = self.movingPiece
            self.board[self.initialRow][self.initialCol] = 0
            enPassant = self.handleEnPassant()
            self.lastMove = [
                (self.initialRow, self.initialCol), (row, col)]
            if enPassant:
                self.lastMove.append(enPassant)
            if isinstance(self.movingPiece, King) and abs(col - self.initialCol) == 2:
                self.castle(row, col)
            if isinstance(self.movingPiece, King) or isinstance(self.movingPiece, Rook):
                self.movingPiece.moved()
            elif isinstance(self.movingPiece, Pawn) and (row == 0 or row == 7):
                self.board[row][col] = Queen(
                    self.movingPiece.user())
            self.currentUser = not self.currentUser
            self.updateOpponent()

    def updateOpponent(self):
        self.client.send(self.lastMove)

    def receiveOpponentData(self):
        while not self.end.is_set():
            with self.threadingLock:
                data = self.client.receive()
                if data:
                    self.updateBoard(data)
                    self.currentUser = not self.currentUser
                else:
                    time.sleep(1)

    def validMoves(self):
        for row in range(8):
            for col in range(8):
                if self.board[row][col] and self.board[row][col].user() == self.player:
                    moves = self.board[row][col].findMoves(
                        self.board, row, col, self.lastMove)
                    if moves:
                        return True
        return False

    def startGame(self):
        self.receiveThread = threading.Thread(target=self.receiveOpponentData)
        self.receiveThread.daemon = True
        self.receiveThread.start()
        offset = None
        while not self.end.is_set():
            self.createBoard()
            self.showLastMove()
            self.showMoves()
            self.showPieces()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.client.close()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    row, col = y//SQUARE_SIZE, x//SQUARE_SIZE
                    if self.myTurn() and self.board[row][col] and self.board[row][col].user() == self.currentUser:
                        self.movingPiece = self.board[row][col]
                        self.initialRow, self.initialCol = row, col
                        offset = [x - col * SQUARE_SIZE, y - row * SQUARE_SIZE]
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.movingPiece:
                        x, y = event.pos
                        row, col = y//SQUARE_SIZE, x//SQUARE_SIZE
                        self.handleMove(row, col)
                        self.movingPiece = None
            if self.movingPiece:
                x, y = pygame.mouse.get_pos()
                self.screen.blit(self.movingPiece.png(),
                                 (x - offset[0], y - offset[1]))
            pygame.display.update()
        self.receiveThread.join()
        self.client.close()
        return self.message
