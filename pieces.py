import os
import pygame


class Pieces:
    """ A superclass for any chess piece. """

    def __init__(self, player, name):
        """Initializes a chess piece and loads/resizes the image corresponding to it.

        Args:
            player (int): The player number for the piece (0 for white, 1 for black)
            name (str): The name of the chess piece.
        """
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
        """ Tests if a player's King is in check.

        Args:
            board (list): A 2D list representing the current board state and the pieces on it.
            r (int): The row index of a piece.
            c (int): The column index of a piece.
            lastMove (list[tuple]): A list of tuples representing the coordinates for the last move.
            removePiece (int, optional): 0 to keep piece on board and check if a potential move gets King out of check. 1 to take piece off board and test if moving piece puts King in check. Defaults to 1.

        Returns:
            bool: True if player's King is now in check, False otherwise.
        """
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
        """ Identify moves for the piece at (r,c) that get it out of check

        Returns:
            list[tuple]: A list of valid moves that a piece can move to
        """
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
        """
        This method is called by all pieces, except the pawn, to identify possible moves. 
        The arguments below explain how this method adjusts to different pieces and functions.

        Args:
            board (list): A 2D list representing the board and the pieces on it.
            row (int): The x-coordinate of a chess piece.
            col (int): The y-coordinate of a chess piece.
            directions (list[tuple]): The list of directions, relative to the current coordinate, that the piece can move to.
            repeating (bool): Instructs whether piece goes in that direction until reaching a piece or going out of bounds.
            lastMove (list[tuple]): A list with coordinates from the previous move. Used by the pawn for en passant.
            testingCheck (bool): 0 if method called by a piece, and 1 if called by checksKing(). Prevents infinite loop.

        Returns:
            list[tuple]: A list of tuples representing the coordinates that the piece can move to.
        """
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

        if isinstance(board[row][col], King):
            if board[row][col].unmoved:
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


class King(Pieces):
    """
        The King and Rook class both keep track of whether the piece has been moved to check for castling.
    """

    def __init__(self, player):
        super().__init__(player, "king")
        self.unmoved = True

    def moved(self):
        self.unmoved = False

    def findMoves(self, board, row, col, lastMove, testingCheck=0):
        """
        Like the other pieces, it has a list of directions that the King can possibly move in. 
        The piece calls the superclass method, which will return valid moves from castling or any of the directions

        Returns:
            list[tuple]: A list of valid moves that won't place the king in check.
        """
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        return super().findMoves(board, row, col, directions, 0, lastMove, testingCheck)


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
        """
        Sets the direction the pawn moves in based on what player it is.
        If still in starting row, test to see if it can move two spaces.
        Use lastMove to identify if enPassant is a viable option.
        """
        moves = []
        direction = -1 if self.player == 0 else 1

        # If method not called by checksKing() and moving the pawn places King in check, identify safe moves.
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
