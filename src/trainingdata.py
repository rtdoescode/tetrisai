import numpy as np
from numpy import array
import json

class TrainingSample(object):

    samplelist = []

    def __init__(self, board, action, reward):
        self.board = board
        self.action = action
        self.reward = reward
        self.previous_rotation = None

    @staticmethod
    def add_training_data(data):
        TrainingSample.samplelist.append(data)

    @staticmethod
    def log_training_data(amount):
        f = open("data\datadump.txt", "w")

        startpos = len(TrainingSample.samplelist) - amount
        startpos = max(0, startpos)

        for i in range(startpos, len(TrainingSample.samplelist)):

            sample = TrainingSample.samplelist[i]
            f.write("\n"+repr(i) + ": BOARD=\n")

            counter = 0
            while counter < 21:
                if counter == 7 or counter == 11:
                    f.write("\n")
                f.write(repr(int(sample.board[0][counter])) + ", ")
                counter+=1

            f.write("\nACTION=\n")
            f.write(repr(sample.action))
            f.write("\nREWARD=\n")
            f.write(repr(sample.reward) + "\n")

        f.close()


    @staticmethod
    def flush_training_data():
        del TrainingSample.samplelist
        TrainingSample.samplelist = []