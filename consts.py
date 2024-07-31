"""
  Specifies constants for board and message screens. 
  These values can be modified to change the displayed colors and board sizing.
"""

WIDTH, HEIGHT = 800, 800

ROWS, COLS = 8, 8

COLOR_OPTIONS = [(255, 206, 158), (209, 139, 71),  # chess board colors
                 (212, 220, 139), (118, 150, 86),  # valid move colors
                 (222, 184, 135), (139, 69, 19),   # message screen colors
                 (204, 183, 174), (112, 102, 119)]  # last move colors

SQUARE_SIZE = WIDTH // ROWS

BUTTON_WIDTH = 420

BUTTON_HEIGHT = 180
