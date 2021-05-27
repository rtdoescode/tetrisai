# This file was not implemented by me and was obtained from GitHub and modified slightly.
# https://gist.github.com/silvasur/565419
# The stop_game() method is the only method in this file 

# Copyright (c) 2010 "Laria Carolin Chabowski"<me@laria.me>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import os
from random import randrange as rand

# The configuration
cell_size = 18
cols = 10
rows = 22
maxfps = 30

colors = [
    (0, 0, 0),
    (255, 85, 85),
    (100, 200, 115),
    (120, 108, 245),
    (255, 140, 50),
    (50, 120, 52),
    (146, 202, 73),
    (150, 161, 218),
    (35, 35, 35)  # Helper color for background grid
]

# Define the shapes of the single parts
tetris_shapes = [
    [[0, 1, 0],
     [1, 1, 1]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]


def rotate_clockwise(shape):
    return [[shape[y][x]
             for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for i in range(cols)]] + board


def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def new_board():
    board = [[0 for x in range(cols)]
             for y in range(rows)]
    board += [[1 for x in range(cols)]]
    return board


class MinimalTetrisApp(object):
    def __init__(self, agent):
        self.width = cell_size * (cols + 6)
        self.height = cell_size * rows
        self.rlim = cell_size * cols
        self.bground_grid = [[8 if x % 2 == y % 2 else 0 for x in range(cols)] for y in range(rows)]

        self.ai_ready = False
        self.demo_game = False
        self.agent = agent
        self.game_already_stopped = False
        self.last_stone_type = None
        agent.tetris = self

        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.init_game()

    def set_agent(self, agent):
        self.agent = agent
        self.agent.tetris = self

    def ai_step(self):
        self.moves += 1
        if self.agent and self.ai_ready:
            self.agent.take_action()
        elif not self.ai_ready:
            print("ai step called not ready")
        else:
            print("ai step called with no agent")

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.last_stone_type = rand(len(tetris_shapes))
        self.next_stone = tetris_shapes[self.last_stone_type]
        self.stone_x = int(cols / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.gameover = True
            # self.stop_game()

        # Whenever a new stones is selected the network needs to decide where to place it
        if not self.gameover:
            self.ai_step()

    def init_game(self):
        self.moves = 0
        self.board = new_board()
        self.level = 1
        self.score = 0
        self.lines = 0

        self.gameover = False
        self.paused = False

        # tell the ai to start
        self.ai_ready = True
        self.new_stone()

    def add_cl_lines(self, n):

        #if n > 0:
        #    print("LINES INCREMENT")

        #print("lines now at "+repr(self.lines))
        #    f = open("gamelogs.txt", "a")
        #    f.write("LINECLEAR " + repr(n) + "\n")
        linescores = [0, 60, 100, 300, 1200]
        self.lines += n
        self.score += linescores[n] * self.level
        if self.lines >= self.level * 6:
            self.level += 1
            newdelay = 1000 - 50 * (self.level - 1)
            newdelay = 100 if newdelay < 100 else newdelay

    def move(self, delta_x):
        if not self.gameover and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not check_collision(self.board,
                                   self.stone,
                                   (new_x, self.stone_y)):
                self.stone_x = new_x

    def drop(self, manual):
        if not self.gameover and not self.paused:
            self.score += 1 if manual else 0
            self.stone_y += 1
            if check_collision(self.board,
                               self.stone,
                               (self.stone_x, self.stone_y)):
                self.board = join_matrixes(
                    self.board,
                    self.stone,
                    (self.stone_x, self.stone_y))
                self.new_stone()
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(
                                self.board, i)
                            cleared_rows += 1
                            break
                    else:
                        break
                self.add_cl_lines(cleared_rows)
                return True
        return False

    def insta_drop(self):
        if not self.gameover and not self.paused:
            while (not self.drop(True)):
                pass

    def rotate_stone(self):
        if not self.gameover and not self.paused:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def toggle_pause(self):
        self.paused = not self.paused

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def stop_game(self):
        # print("printing game data")

        if not os.path.isfile("data\gamelogs.csv"):
            f = open("data\gamelogs.csv", "a")
            f.write("lines, score, moves" + "\n")

        gamestring = repr(self.lines) + "," + repr(self.score) + "," + repr(self.moves)
        f = open("data\gamelogs.csv", "a")
        f.write(gamestring + "\n")
        f.close()
        return
