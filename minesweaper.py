from random import randint
import sys
import time
import pygame
import pygame.freetype

pygame.init()


class Cell:
    def __init__(self):
        self.click = False
        self.mine = randint(0, 10) == 10
        self.flagged = False
        self.near_mines = 0

    def __repr__(self):
        return f"{self.click}.{self.mine}.{self.flagged}.{self.near_mines}"

    def clicked(self):
        self.click = True
        self.flagged = False

    def flag(self):
        self.flagged = not self.flagged

    def mine_counter(self):
        if self.mine:
            self.near_mines = 0
        else:
            self.near_mines += 1

    def is_clicked(self):
        return self.click

    def is_mine(self):
        return self.mine

    def is_flagged(self):
        return self.flagged

    def mine_count(self):
        return self.near_mines


class Mine_Matrix:
    def __init__(self, mine_area, window, window_size):
        self.game_font = pygame.freetype.Font(
            "/System/Library/Fonts/Menlo.ttc", 10)
        self.window = window
        self.window_size = window_size
        self.mine_area = mine_area
        self.cell_size = 24
        self.matrix = []
        self.row_len = self.mine_area[1] // self.cell_size
        self.col_len = self.mine_area[0] // self.cell_size
        self.mine_count = 0
        self.flag_count = 0
        self.mine_countdown = 0
        self.checked_cells = set()

        self.mine_top = self.window_size[1] - self.mine_area[1] - 18
        self.mine_right = self.mine_area[0] + 18
        self.mine_bottom = self.window_size[1] - 18
        self.mine_left = 18

        self.mine_colour = (0, 0, 0)
        self.flag_colour = (200, 100, 0)
        self.light_bevel_colour = (255, 255, 255)
        self.dark_bevel_colour = (128, 128, 128)
        self.dark_bevel_colour2 = (165, 165, 165)
        self.cell_colour = (192, 192, 192)
        self.mine_area = (216, 216)

    def validated_mouse(self, mouse_pos):
        if ((self.mine_left <= mouse_pos[0] < self.mine_right) and
                (self.mine_top <= mouse_pos[1] < self.mine_bottom)):
            return ((mouse_pos[1] - self.mine_top) // self.cell_size,
                    (mouse_pos[0] - self.mine_left) // self.cell_size)
        else:
            return False

    def create_matrix(self):
        self.matrix = []

        # Create cell matrix
        for _ in range(0, self.mine_area[1], self.cell_size):
            line = []
            for _ in range(0, self.mine_area[0], self.cell_size):
                cell = Cell()
                if cell.is_mine():
                    self.mine_count += 1
                line.append(cell)

            self.matrix.append(line)

        # Generate count of mines in area
        for row, _ in enumerate(self.matrix):
            for col, _ in enumerate(self.matrix[0]):
                # Loop through neighbouring matrix
                for new_row in range(max(0, row-1),
                                     min(self.row_len-1, row + 1) + 1):
                    for new_col in range(max(0, col-1),
                                         min(self.col_len-1, col + 1) + 1):

                        # increment mine count
                        if self.matrix[new_row][new_col].is_mine():
                            self.matrix[row][col].mine_counter()

        self.mine_countdown = self.mine_count - self.flag_count

    def draw_3d_cell(self, left, top, flagged):
        if flagged:
            pygame.draw.rect(self.window, self.flag_colour, pygame.Rect(
                left, top, self.cell_size, self.cell_size))
        # Bright edge
        pygame.draw.polygon(self.window, self.light_bevel_colour,
                            ((left, top),
                             (left+self.cell_size, top),
                             (left+self.cell_size-3, top+3),
                             (left+3, top+3),
                             (left+3, top+self.cell_size-3),
                             (left, top+self.cell_size)))
        # Dark edge
        pygame.draw.polygon(self.window, self.dark_bevel_colour,
                            ((left+self.cell_size, top),
                             (left+self.cell_size, top+self.cell_size),
                             (left, top+self.cell_size),
                             (left + 3, top+self.cell_size-3),
                             (left+self.cell_size-3,
                              top+self.cell_size-3),
                             (left+self.cell_size-3, top+3)))

    def draw_2d_cell(self, left, top, mine_count, mine):
        # Outer line
        pygame.draw.polygon(self.window, self.dark_bevel_colour,
                            ((left, top),
                             (left+self.cell_size, top),
                             (left+self.cell_size, top+1),
                             (left+1, top+1),
                             (left+1, top+self.cell_size),
                             (left, top+self.cell_size)))

        # Inner line
        pygame.draw.polygon(self.window, self.dark_bevel_colour2,
                            ((left+1, top+1),
                             (left+self.cell_size, top+1),
                             (left+self.cell_size, top+1),
                             (left+1, top+2),
                             (left+1, top+self.cell_size),
                             (left+1, top+self.cell_size)))

        if mine_count > 0:
            self.game_font.render_to(self.window,
                                     (left + (self.cell_size//2) - 2,
                                      top + (self.cell_size//2) - 2),
                                     str(mine_count),
                                     (255, 0, 0))
        if mine:
            pygame.draw.rect(self.window, self.mine_colour, pygame.Rect(
                left, top, self.cell_size, self.cell_size))

    def draw_mine_matrix(self):
        # Loop through x,y cordinates
        for top in range(self.mine_top,
                         self.mine_top + self.mine_area[1],
                         self.cell_size):
            for left in range(self.mine_left,
                              self.mine_left + self.mine_area[0],
                              self.cell_size):

                # Normalise coordinates to matrix indexes
                check_top = (top - self.mine_top) // self.cell_size
                check_left = (left - self.mine_left) // self.cell_size

                # If not clicked, draw 3D version
                if not self.matrix[check_top][check_left].is_clicked():
                    self.draw_3d_cell(left,
                                      top,
                                      self.matrix[check_top][check_left].is_flagged())

                # If clicked, draw 2D version
                else:
                    self.draw_2d_cell(left,
                                      top,
                                      self.matrix[
                                          check_top][check_left].mine_count(),
                                      self.matrix[check_top][
                                          check_left].is_mine())

    def flagged(self, mouse_pos):
        # Change flag status if right button is clicked
        if index := self.validated_mouse(mouse_pos):

            # If the cell was already flagged then decrement flag count
            if self.matrix[index[0]][index[1]].is_flagged():
                # make sure not to go into negative mine numbers
                self.flag_count -= 1

            # If cell was not flagged already then increment flag count
            elif not self.matrix[index[0]][index[1]].is_flagged():
                self.flag_count += 1

            # Switch flag
            self.matrix[index[0]][index[1]].flag()
            print(self.mine_countdown)
            self.mine_countdown = max(0, self.mine_count - self.flag_count)

            # Check return True if the flagged cell is a mine
            if self.matrix[index[0]][index[1]].is_mine():
                return True
            return False

    def clicked(self, mouse_pos):
        # Change clicked status if left button is clicked
        if index := self.validated_mouse(mouse_pos):

            # Reveal cell and surrounding cells
            if not self.open_space(index[0], index[1]):
                return False
                # If revealed cell is a mine, end game
                # self.end_game()
            return True

    def open_space(self, row, col):
        # Reveal cell and recursively reveal adjacent empty cells

        # If it's a mine, lose game
        if self.matrix[row][col].is_mine():
            return False

        # Open cell
        self.matrix[row][col].clicked()

        # Remove from flag count
        if self.matrix[row][col].is_flagged():
            self.flag_count -= 1

        # If cell has a mine count, return
        if self.matrix[row][col].mine_count() > 0:
            return True

        # If cell has no count then click surrounding cells
        for new_row in range(max(0, row-1),
                             min(self.row_len-1, row + 1) + 1):
            for new_col in range(max(0, col-1),
                                 min(self.col_len-1, col + 1) + 1):
                if self.matrix[new_row][new_col].is_clicked():
                    continue
                self.open_space(new_row, new_col)

        return True

    def numbers(self, timer, mines):

        font = pygame.freetype.Font(
            "/Users/Home/Library/Fonts/DS-DIGII.TTF", 35)
        font.render_to(self.window, (self.window_size[0] - 80, 40),
                       timer, (255, 0, 0))
        font.render_to(self.window, (20, 40),
                       mines, (255, 0, 0))

    def end_game(self):
        # Game is lost, reveal all cells
        for row in self.matrix:
            for cell in row:
                cell.clicked()
        # print("loss")
        # font = pygame.freetype.Font(
        #     "/Users/Home/Library/Fonts/DS-DIGII.TTF", 100)
        # font.render_to(self.window,
        #                (20, 40),
        #                "You lost!!", (255, 0, 0))

    def validate_win(self):
        validated = False
        for row in self.matrix:
            for cell in row:
                if cell.is_mine() and cell.is_flagged():
                    validated = True
                elif cell.is_mine() and not cell.is_flagged():
                    validated = False
        return validated

    def win(self):
        print("win")
        font = pygame.freetype.Font(
            "/Users/Home/Library/Fonts/DS-DIGII.TTF", 100)
        font.render_to(self.window,
                       (50, 50),
                       "You Won!!", (255, 0, 0))


def main():
    # Pygame variables
    # fps = 60
    window_size = (252, 314)  # (x,y)
    background_colour = (192, 192, 192)

    size = (9, 9)  # number of cells
    mine_area = (24 * size[0], 24 * size[1])  # (x,y)

    # Create pygame window
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Minesweaper")

    mine_matrix = Mine_Matrix(mine_area, window, window_size)
    mine_matrix.create_matrix()

    start = False
    start_time = 0.0
    timer = "000"
    mines = "000"

    while True:
        # Quit when quit event is triggered
        for event in pygame.event.get():
            # Quit game
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not start:
                    start = True
                    start_time = time.time()

                # Left click to reveal cell
                if pygame.mouse.get_pressed() == (1, 0, 0):
                    if not mine_matrix.clicked(pygame.mouse.get_pos()):
                        start = False
                        # Save latest time and mine count to
                        # be displayed when game is won
                        timer = str(int(time.time() - start_time)).zfill(3)
                        mines = str(mine_matrix.mine_countdown).zfill(3)

                        # Eng the game
                        mine_matrix.end_game()

                # Right click to flag cell
                elif pygame.mouse.get_pressed() == (0, 0, 1):
                    # If mine is flagged check if all mines are flagged
                    if mine_matrix.flagged(pygame.mouse.get_pos()):
                        # If all mines are flagged, then game won
                        if mine_matrix.validate_win():
                            start = False
                            # Save latest time and mine count to
                            # be displayed when game is won
                            timer = str(int(time.time() - start_time)).zfill(3)
                            mines = str(mine_matrix.mine_countdown).zfill(3)

                            # Eng the game
                            mine_matrix.end_game()

        # Draw background
        window.fill(background_colour)

        # Draw clock and mine counter
        if start:
            # Create "000" format for time counter
            timer = str(int(time.time() - start_time)).zfill(3)

            # Create "000" format for mines
            mines = str(mine_matrix.mine_countdown).zfill(3)

            mine_matrix.numbers(timer, mines)
        else:
            mine_matrix.numbers(timer, mines)

        # Draw minefield
        mine_matrix.draw_mine_matrix()

        # Reset game with 'c'
        if pygame.key.get_pressed()[pygame.K_c]:
            # Reset timers and mine count
            timer = "000"
            mines = "000"

            # Generate a new mine matrix
            mine_matrix = Mine_Matrix(mine_area, window, window_size)
            mine_matrix.create_matrix()

        # # Refresh window
        pygame.display.flip()


if __name__ == '__main__':
    main()
