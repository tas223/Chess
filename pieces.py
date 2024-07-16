import os
import pygame


class Pieces:
    def __init__(self, player, name):
        self.player = player
        self.color = "white" if player == 0 else "black"
        self.name = name
        self.image = pygame.transform.scale(pygame.image.load(
            os.path.join(f'images/{self.color}_{self.name}.png')), (75, 75))

    def png(self):
        return self.image

    def user(self):
        return self.player

    def checksKing(self, board, r, c, lastMove, removePiece=1):
        piece = board[r][c]
        if not isinstance(board[r][c], King) and removePiece:
            board[r][c] = 0
        for row in range(8):
            for col in range(8):
                if board[row][col] and board[row][col].user() != piece.user():
                    for x, y in board[row][col].findMoves(board, row, col, lastMove, 1):
                        if isinstance(board[x][y], King) and board[x][y].user() == piece.user():
                            board[r][c] = piece
                            return True
        board[r][c] = piece
        return False

    def movesInCheck(self, board, r, c, lastMove):
        originalMoves = board[r][c].findMoves(board, r, c, lastMove, 1)
        moves = []
        for x, y in originalMoves:
            temp = board[x][y]
            board[x][y] = board[r][c]
            board[r][c] = 0
            if not self.checksKing(board, x, y, lastMove, 0):
                moves.append((x, y))
            board[r][c] = board[x][y]
            board[x][y] = temp
        return moves

    def findMoves(self, board, row, col, directions, repeating, lastMove, testingCheck):
        moves = []
        if not testingCheck and isinstance(board[row][col], King):
            return self.movesInCheck(board, row, col, lastMove)
        elif not testingCheck:
            if self.checksKing(board, row, col, lastMove) == True:
                return self.movesInCheck(board, row, col, lastMove)

        for x, y in directions:
            newRow, newCol = row + x, col + y
            if repeating:
                while 0 <= newRow < 8 and 0 <= newCol < 8:
                    if board[newRow][newCol] == 0 or board[newRow][newCol].user() != self.player:
                        moves.append((newRow, newCol))
                    if board[newRow][newCol] != 0:
                        break
                    newRow, newCol = newRow + x, newCol + y
            else:
                if 0 <= newRow < 8 and 0 <= newCol < 8:
                    if board[newRow][newCol] == 0 or board[newRow][newCol].user() != self.player:
                        moves.append((newRow, newCol))
        return moves


class King(Pieces):
    def __init__(self, player):
        super().__init__(player, "king")
        self.unmoved = True

    def moved(self):
        self.unmoved = False

    def findMoves(self, board, row, col, lastMove, testingCheck=0):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        moves = super().findMoves(board, row, col, directions, 0, lastMove, testingCheck)

        if self.unmoved:
            if board[row][0] and isinstance(board[row][0], Rook) and board[row][0].unmoved:
                for column in range(1, 4):
                    if board[row][column] != 0:
                        break
                    if column == 3:
                        moves.append((row, 2))
            if board[row][7] and isinstance(board[row][7], Rook) and board[row][7].unmoved:
                for column in range(5, 7):
                    if board[row][column] != 0:
                        break
                    if column == 6:
                        moves.append((row, 6))
        return moves


class Queen(Pieces):
    def __init__(self, player):
        super().__init__(player, "queen")

    def findMoves(self, board, row, col, lastMove, testingCheck=0):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        return super().findMoves(board, row, col, directions, 1, lastMove, testingCheck)


class Rook(Pieces):
    def __init__(self, player):
        super().__init__(player, "rook")
        self.unmoved = True

    def moved(self):
        self.unmoved = False

    def findMoves(self, board, row, col, lastMove, testingCheck=0):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        return super().findMoves(board, row, col, directions, 1, lastMove, testingCheck)


class Knight(Pieces):
    def __init__(self, player):
        super().__init__(player, "knight")

    def findMoves(self, board, row, col, lastMove, testingCheck=0):
        directions = [(-2, 1), (2, -1), (-2, -1), (2, 1),
                      (1, 2), (-1, -2), (-1, 2), (1, -2)]
        return super().findMoves(board, row, col, directions, 0, lastMove, testingCheck)


class Bishop(Pieces):
    def __init__(self, player):
        super().__init__(player, "bishop")

    def findMoves(self, board, row, col, lastMove, testingCheck=0):
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        return super().findMoves(board, row, col, directions, 1, lastMove, testingCheck)


class Pawn(Pieces):
    def __init__(self, player):
        super().__init__(player, "pawn")

    def findMoves(self, board, row, col, lastMove, testingCheck=0):
        moves = []
        direction = -1 if self.player == 0 else 1

        if not testingCheck:
            if self.checksKing(board, row, col, lastMove) == True:
                return self.movesInCheck(board, row, col, lastMove)

        newRow = row + direction
        if newRow < 8:
            if board[newRow][col] == 0:
                moves.append((newRow, col))
            if 0 <= col - 1 and board[newRow][col - 1] != 0 and board[newRow][col - 1].user() != self.player:
                moves.append((newRow, col - 1))
            if col + 1 < 8 and board[newRow][col + 1] != 0 and board[newRow][col + 1].user() != self.player:
                moves.append((newRow, col + 1))

        newRow = row + 2*direction
        if ((self.player == 0 and row == 6) or (self.player == 1 and row == 1)) and board[newRow - direction][col] == 0 and board[newRow][col] == 0:
            moves.append((newRow, col))

        enPassantRow = 3 if self.player == 0 else 4
        if row == enPassantRow and len(lastMove) == 2:
            initialX, initialY = lastMove[0]
            finalX, finalY = lastMove[1]
            if isinstance(board[finalX][finalY], Pawn) and abs(finalX - initialX) == 2 and finalY == initialY and row == finalX and abs(finalY - col) == 1:
                moves.append((row + direction, finalY))
        return moves
