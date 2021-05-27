from keras.models import Sequential, load_model
from keras.layers import Dense, Activation
from keras.optimizers import Adam

class Model(object):

    def __init__(self):
        self.nn_model = None
        self.layercount = 7
        self.layersize = 32
        self.output_size = 11
        self.input_size = 21
        self.modelfilename = 'data\model.h5'

        self.setup()

    def save(self):
        if self.nn_model:
            self.nn_model.save(self.modelfilename)

    def load(self):
        self.nn_model = load_model(self.modelfilename)

    def setup(self):

        try:
            self.load()
            print("Model loaded.")

            return
        except:
            print("Could not load model. Creating new model.")

        # create model
        self.nn_model = Sequential()

        self.nn_model.add(Dense(64, input_dim=self.input_size, activation='relu', kernel_initializer='glorot_uniform'))

        for x in range(0, self.layercount):
            self.nn_model.add(Dense(self.layersize, activation='relu', kernel_initializer='glorot_uniform'))

        self.nn_model.add(Dense(self.output_size, activation='relu', kernel_initializer='glorot_uniform'))
        self.nn_model.compile(loss='mse', optimizer=Adam())