from lenet import LeNet
from keras.models import load_model
from keras.utils import Sequence

from sklearn.utils import shuffle
import numpy as np
import math as m

import matplotlib.image as mpimg


class SteeringAnglePredictor:
    def __init__(self, img_shape=(160,320,3), model_file="lenet.h5",  prev_model=None, batch_size=128, epochs=5):
        # net = NvidiaNet()
        net = LeNet()
        self.nnModel = net.network(img_shape=img_shape)
        self.modelLoaded = False
        self.modelFile = model_file
        self.prevModel = prev_model
        self.batchSize = batch_size
        self.epochs = epochs

    class DataSequence(Sequence):
        def __init__(self, x_set, y_set, batch_size):
            self.x, self.y = shuffle(x_set, y_set)
            self.batch_size = batch_size

        def __len__(self):
            return int(m.ceil(len(self.x) / float(self.batch_size)))

        def __getitem__(self, idx):
            batch_x = self.x[idx * self.batch_size:(idx + 1) * self.batch_size]
            batch_y = self.y[idx * self.batch_size:(idx + 1) * self.batch_size]

            return shuffle(np.array([mpimg.imread(file_name) for file_name in batch_x]), np.array(batch_y))

    def train(self, X, y, overwrite_model=True):
        X_train, X_valid, y_train, y_valid = self.train_validation_split(X, y)

        if self.prevModel is not None:
            self.nnModel = load_model(self.prevModel)

        self.nnModel.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])

        history = self.nnModel.fit_generator(generator=self.DataSequence(X_train, y_train, self.batchSize) ,
                                             epochs=self.epochs, validation_data=self.DataSequence(X_valid, y_valid, self.batchSize),
                                             shuffle=True, verbose=1)

        self.nnModel.save(filepath=self.modelFile, overwrite=overwrite_model)
        self.modelLoaded = True
        return history

    def train_validation_split(self, X, y, valid_split=0.2):
        X, y = shuffle(X, y)
        valid_len = m.ceil(valid_split * len(X))
        X_valid, y_valid = X[0:valid_len], y[0:valid_len]
        X_train, y_train = X[valid_len:], y[valid_len:]
        return X_train, X_valid, y_train, y_valid

    def test(self, x, y):
        if not self.modelLoaded:
            self.nnModel = load_model(self.modelFile)

        for i in range(len(x)):
            im = mpimg.imread(x[i], format="RGB")
            pred = self.nnModel.predict(np.array([im]), batch_size=1)
            print("pred {}, real {}".format(pred, y[i]))

        # metrics = self.nnModel.evaluate(X_test, y_test)
        # for metric_i in range(len(self.nnModel.metrics_names)):
        #     metric_name = self.nnModel.metrics_names[metric_i]
        #     metric_value = metrics[metric_i]
        #     print('{}: {}'.format(metric_name, metric_value))
        # return metrics


