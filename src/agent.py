from game import TetrisApp
from copy import copy, deepcopy
from trainingdata import TrainingSample
import numpy as np
from ConsoleHelper import ConsoleHelper as ch


class Agent(object):

    def __init__(self, random):
        self.prevscore = 0
        self.prevlines = 0
        self.prevheight = 0
        self.prevholes = 0
        self.prevbump = 0

        self.consecutive_rotations = 0

        self.manager = None
        self.data = None
        self.tetris = None
        self.randommoves = random

    def get_inputs(self):

        inputs = np.zeros([1, 21])

        # input part stone
        inputs[0][self.tetris.last_stone_type] = 1

        # input part rotation
        inputs[0][7+self.consecutive_rotations] = 1

        # input part heights
        for i in range(10):
            inputs[0][i+11] = self.get_height_for_col(i)

        return inputs

    def get_height_for_col(self, col):

        current_height = len(self.tetris.board)-1
        # print("max height: " + repr(current_height))

        for row in range(23):
            # print("col " + repr(col) + " row " + repr(row))
            if self.tetris.board[row][col] != 0:
                # print("RETURN col " + repr(col) + " height " + repr(current_height))
                return current_height
            current_height -= 1

    def get_height(self):

        current_height = len(self.tetris.board)

        for row in self.tetris.board:
            for column in row:
                if column != 0:
                    return current_height
            current_height -= 1

    def get_holes(self):

        holes = 0

        for x in range(1, 22):
            for y in range(10):
                if self.tetris.board[x][y] == 0 and self.tetris.board[x - 1][y] > 0:
                    #print("hole at " + repr(x) + ", " + repr(y))
                    holes += 1

        return holes

    def get_reward(self):

        lines_reward_multiplier = 2
        holes_reward_multiplier = 10
        height_reward_multiplier = 10

        # The reward should never be negative
        # The worst possible move (I think) is 3 holes generated and 3 height added
        # Ensure that reward starts higher than 3*height_reward_multiplier + 3*holes_reward_multiplier
        reward = 100

        # add reward based on lines cleared
        lines = self.tetris.lines - self.prevlines
        linescores = [0, 40, 100, 300, 1200]
        reward += linescores[lines]*lines_reward_multiplier

        # subtract reward based on height added
        height = self.get_height()
        height_change = height - self.prevheight
        reward -= height_change*height_reward_multiplier

        # subtract reward based on holes
        holes = self.get_holes()
        holes_change = holes - self.prevholes
        holes_change = max(holes_change, 0)

        reward -= holes_change*holes_reward_multiplier

        if self.consecutive_rotations > 3:
            reward -= 1000

        current_score = self.tetris.score
        score_increase = current_score - self.prevscore

        self.prevholes = holes
        self.prevlines = self.tetris.lines
        self.prevscore = current_score
        self.prevheight = height

        return reward

    def perform_move(self, move):

        if move == 0:
            self.consecutive_rotations = 0
            self.tetris.move(-3)
            self.tetris.insta_drop()
            return
        if move == 1:
            self.consecutive_rotations = 0
            self.tetris.move(-2)
            self.tetris.insta_drop()
            return
        if move == 2:
            self.consecutive_rotations = 0
            self.tetris.move(-1)
            self.tetris.insta_drop()
            return
        if move == 3:
            self.consecutive_rotations = 0
            self.tetris.insta_drop()
            return
        if move == 4:
            self.consecutive_rotations = 0
            self.tetris.move(+1)
            self.tetris.insta_drop()
            return
        if move == 5:
            self.consecutive_rotations = 0
            self.tetris.move(+2)
            self.tetris.insta_drop()
            return
        if move == 6:
            self.consecutive_rotations = 0
            self.tetris.move(+3)
            self.tetris.insta_drop()
            return
        if move == 7:
            self.consecutive_rotations = 0
            self.tetris.move(+4)
            self.tetris.insta_drop()
            return
        if move == 8:
            self.consecutive_rotations = 0
            self.tetris.move(+5)
            self.tetris.insta_drop()
            return
        if move == 9:
            self.consecutive_rotations = 0
            self.tetris.move(+6)
            self.tetris.insta_drop()
            return
        if move == 10:
            self.consecutive_rotations += 1
            self.tetris.rotate_stone()
            self.take_action(last_was_rotation=True)
            return

    def rotation_reward(self, reward):
        return reward/2

    def take_action(self, last_was_rotation=False):

        reward = self.get_reward()
        rot_data = None

        # Add reward to previous training sample
        if self.data:
            if not last_was_rotation:

                self.data.reward = reward
                # add this training sample to the pool
                TrainingSample.add_training_data(self.data)

                # add rewards for previous rotations
                rreward = reward
                rdata = self.data
                # reward is reduced to 75% for each rotation                # to discourage AI from endlessly rotating
                while rdata.previous_rotation:
                    rdata = rdata.previous_rotation
                    rreward = reward*0.75
                    rdata.reward = rreward
            else:
                TrainingSample.add_training_data(self.data)
                rot_data = self.data

            self.data = None

        input = self.get_inputs()
        move = None

        if self.randommoves:
            move = np.random.random_integers(0, 10)
        else:
            actions = self.manager.model.nn_model.predict(input)
            move = actions.argmax()

        self.data = TrainingSample(input, move, None)

        if rot_data:
            self.data.previous_rotation = rot_data

        # Print progress reports after every 100 samples
        if len(TrainingSample.samplelist)%100 == 0:
            ch.printHelper("yellow", repr(len(TrainingSample.samplelist)) + " training moves recorded.")

        self.perform_move(move)