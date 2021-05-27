from keras.layers import Dense, Activation
from keras.models import Sequential, load_model
from model import Model
from agent import Agent
from game import TetrisApp
from stripped_game import MinimalTetrisApp
from trainingdata import TrainingSample
import numpy as np
from numpy import array
from ConsoleHelper import ConsoleHelper as ch


class TrainingManager(object):

    def __init__(self):
        self.save_training_data = True
        self.minimum_reward_threshold = 80
        self.max_saved_training_data = 100
        self.random_agent_movement = True
        self.run()

    def run(self):
        self.model = Model()

        while(True):
            cmd = input("\n'Train' to run training loop\n"
                        "'Exit' to exit program\n")

            cmd = cmd.lower().split(" ")
            #print(cmd)
            if cmd[0] == "train":

                amt = 0

                if len(cmd) > 1:
                    try:
                        amt = int(cmd[1])
                    except ValueError:
                        print("Integer required.")
                        continue
                else:
                    amt = input("Enter number game moves to target:")
                    try:
                        amt = int(amt)
                    except ValueError:
                        print("Integer required.")
                        continue
                self.train_iteration(amt)

            if cmd[0] == "save":
                self.model.save()

            if cmd[0] == "file":
                self.model.save()

            if cmd[0] == "slow":
                self.model.save()

            if cmd[0] == "exit":
                return

    def train_iteration(self,target):
        self.run_model(target, random=self.random_agent_movement)
        self.train_model()

        # Clear used training data
        ch.printHelper("info","Cleaning training data...")
        if self.save_training_data:
            TrainingSample.log_training_data(self.max_saved_training_data)
        TrainingSample.flush_training_data()

        ch.printHelper("info","Saving model...")
        self.model.save()
        #print(len(TrainingSample.samplelist))

    def run_model(self, target, random):
        while len(TrainingSample.samplelist) < target:

            self.agent = Agent(random)
            self.agent.manager = self
            self.agent.model_holder = self.model
            #self.game = TetrisApp(self.agent)
            #ch.printHelper("warn", "starting gamae")
            self.game = MinimalTetrisApp(self.agent)
            self.game.stop_game()
            #self.game.run()

    def train_model(self):

        trainmodel = self.model.nn_model
        X = []
        Y = []
        Z = []

        reward_threshold = 10
        rewards_list = []

        for sample in TrainingSample.samplelist:
            rewards_list.append(sample.reward)

        rewards_list.sort()
        reward_threshold = rewards_list[int(len(rewards_list)*0.8)]

        if reward_threshold > self.minimum_reward_threshold:
            self.minimum_reward_threshold = reward_threshold
        else:
            reward_threshold = self.minimum_reward_threshold
		
        for sample in TrainingSample.samplelist:

            if sample.board is None or sample.action is None or sample.reward is None:
                ch.printHelper("warn", "Malformed training data found")
                del sample
                continue

            if sample.reward >= reward_threshold:
                X.append(sample.board[0])

                y_entry = np.zeros(11)
                y_entry[sample.action] = 1

                Y.append(y_entry)

            else:
                del sample

        np_X = array(X)
        np_Y = array(Y)

        x_len = len(np_X)
        y_len = len(np_Y)

        if not (x_len == y_len):
            ch.printHelper("warn","Unequal training data found")
        else:
            ch.printHelper("success",repr(x_len) + " of " + repr(len(rewards_list)) + " training moves accepted with threshold of " + repr(reward_threshold))

        ch.printHelper("info","Training model...")
        trainmodel.fit(np_X, np_Y, epochs=1, verbose=0)