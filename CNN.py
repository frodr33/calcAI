import keras, io
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
import numpy as np
# import cv2
from PIL import Image
from keras.models import load_model # creates a HDF5 file 'my_model.h5'
from keras.datasets import mnist
import keras
import os
import pickle
import gzip
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import random
import PIL.ImageOps
from collections import deque
os.environ["TF_CPP_MIN_LOG_LEVEL"]="3"
np.set_printoptions(threshold=np.nan)


class CNN():
    def load_data(self):
        try:
            with gzip.open('new_data.pkl.gz', 'rb') as f:
                x_train, y_train = pickle.load(f)
                return (x_train, y_train)
        except:
            pass

        x_train = [] # list of 28x28 uint8 arrays
        y_train = [] # list of labels for corresponding uint8 array
        path ="./TrainingSet"
        numCompleted = 0
        for folder in os.listdir(path):
            perc = "{0:0.1f}".format(numCompleted / len(os.listdir(path)) * 100)
            print(perc + "%")
            size = 0
            try:
                dir = os.listdir(path + "/" + folder)
                for img in dir:
                    image = Image.open(path + "/" + folder + "/" + img)
                    image = PIL.ImageOps.invert(image)
                    resize = image.resize((100,100))
                    resize.load()
                    data = np.asarray(resize, dtype="uint8")
                    x_train.append(data)
                    y_train.append(folder)
                    size += 1
                print(folder)
                print(size)
                numCompleted += 1
            except:
                continue
        y_train = np.asarray(y_train)
        dataset = [x_train, y_train]
        print("Creating pickle file")
        f = gzip.open('./Data/new_data.pkl.gz', 'wb')
        pickle.dump(dataset, f)
        f.close()
        return (x_train, y_train)

    def train(self, x_train, y_train, res_to_int):
        batch_size = 128
        num_classes = 21 #need to be changed
        epochs = 3  

        # input image dimensions
        img_rows, img_cols = 100, 100
        print('x_train shape:', x_train.shape)
        print(x_train.shape[0], 'train samples')

        #Shuffle Lists
        c = list(zip(x_train, y_train))
        random.shuffle(c)
        x_train, y_train = zip(*c)
        x_train = np.array(list(x_train))
        x_train = x_train.reshape(len(x_train),100,100,1)
        y_train = [res_to_int[c] for c in y_train]
        y_train = keras.utils.to_categorical(y_train, num_classes)
        model = Sequential()

        model.add(Conv2D(32, kernel_size=(3, 3),
                        activation='relu',
                        input_shape=(100,100,1)))
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(num_classes, activation='softmax'))
        model.compile(loss=keras.losses.categorical_crossentropy,
                    optimizer=keras.optimizers.Adadelta(),
                    metrics=['accuracy'])
        model.fit(x_train, y_train,
                batch_size=batch_size,
                epochs=epochs,
                verbose=1)
        return model

    def is_whitespace(self, column):
        return int(round(self.pixel_average(column), 1)) + 1 >= 255

    def pixel_average(self, column):
        avg = 0.0
        for pixel in column:
            avg += pixel
        return avg / float(len(column))

    def white(self):
        return 255

    def whitespace(self, columns):
        return [self.white() for _ in range(columns)] 

    def column(self, data, i):
        return [row[i] for row in data]

    def get_columns(self, data):
        columns = []
        colIndex = 0
        while colIndex < len(data[0]):
            column = []
            rowIndex = 0
            while rowIndex < len(data):
                column.append(data[rowIndex][colIndex])
                rowIndex += 1
            colIndex += 1
            columns.append(column)
        return columns

    def add_padding(self, symbol, column):
        if not symbol:
            for pixel in column:
                symbol.append([pixel])
        else:
            index = 0
            while index < len(symbol):
                symbol[index].insert(0, column[index])
                symbol[index].append(column[index])
                index += 1
        return symbol


    def append_column(self, symbol, column):
        if not symbol:
            for pixel in column:
                symbol.append([pixel])
        else:
            index = 0
            while index < len(symbol):
                symbol[index].append(column[index])
                index += 1
        return symbol

    def squarify(self, symbol):
        rows = len(symbol)
        columns = len(symbol[0])
        if rows == columns:
            return symbol
        elif rows < columns:
            squarified = symbol
            while len(squarified) < columns:
                squarified.insert(0, self.whitespace(len(squarified[0])))
                squarified.append(self.whitespace(len(squarified[0])))
            return squarified
        else:
            squarified = symbol
            while len(squarified[0]) < rows:
                squarified = self.add_padding(squarified, self.whitespace(len(squarified)))
            return squarified
        
    def is_operator(self, operators, symbol):
        return symbol in operators

    def evaluate(self, left, right, operator):
        if operator == '+':
            return left + right
        return left - right

    def evaluate_expression(self, operands, operators):
        while len(operators) != 0:
            operator = operators.popleft()
            left = operands.popleft()
            right = operands.popleft()
            operands.appendleft(self.evaluate(left, right, operator))
        return operands.popleft()

    def predict(self, image):
        (x_train, y_train) = self.load_data()
        x_train = np.asarray(x_train)

        # Create label dictionary
        res_to_int = {}
        int_to_res = {}
        counter = 0
        for c in y_train:
            if c not in res_to_int.keys():
                # print(c)
                # print(counter)
                res_to_int[c] = counter
                int_to_res[counter] = c
                counter += 1

        try:
            model = load_model('./Models/final_model.h5')
        except:
            print('Training...')
            model = self.train(x_train, y_train, res_to_int)
            model.save('./Models/final_model.h5')
        
        image = Image.open(image)
        resize = image.resize((100,100))
        data = np.asarray(image, dtype="uint8")
        if len(data.shape) == 3: # make grayscale
            data = data[:,:,0]
        
        columns = []
        for i in range(0, len(data[0])):
            columns.append(self.column(data, i))
        symbols = []
        symbol = []

        for column in columns:
            if self.is_whitespace(column):
                if symbol:  
                    symbols.append(symbol)
                    symbol = []
            else:
                symbol = self.append_column(symbol, column)
        if symbol:
            symbols.append(symbol)
        
        # symbols = [self.squarify(symbol) for symbol in symbols]
        operators = ['+', '-', '*', '/']
        operandQueue = deque()
        operatorQueue = deque()

        for sym in symbols:
            npsym = np.array(sym)
            img = PIL.Image.fromarray(npsym.astype("uint8"))
            image = PIL.ImageOps.invert(img)
            resize = image.resize((100,100))
            plt.imshow(resize, cmap=cm.Greys_r)
            plt.show()      
            resize.load()
            data = np.asarray(resize, dtype="uint8")
            data_4D = data.reshape(1,100,100,1)
            pr = model.predict_classes(data_4D)[0]
            result = int_to_res[pr]
            print(result)
            if self.is_operator(operators, result):
                operatorQueue.append(result)
            else:
                try:
                    operandQueue.append(int(result))
                except:
                    continue
        
        if len(operatorQueue) < len(operandQueue):
            print(operatorQueue)
            print(operandQueue)
            print('Result: ' + str(self.evaluate_expression(operandQueue, operatorQueue)))
        else:
            print('That is not a valid mathematical expression. Try again!')    

    def test(self):
        (x_train, y_train) = self.load_data()
        x_train = np.asarray(x_train)

        # Create label dictionary
        res_to_int = {}
        int_to_res = {}
        counter = 0
        for c in y_train:
            if c not in res_to_int.keys():
                # print(c)
                # print(counter)
                res_to_int[c] = counter
                int_to_res[counter] = c
                counter += 1

        try:
            model = load_model('./Models/new_model.h5')
        except:
            print('Training...')
            model = self.train(x_train, y_train, res_to_int)
            model.save('./Models/new_model.h5')

        numWrong = 0
        lst = ["1", "2","3","4","5","6","7","8","9","+","-"]
        wrongVals = []
        for v in lst:
            path = "TestSet/" + str(v) + "_2.jpg"
            image = Image.open(path)
            image = PIL.ImageOps.invert(image)
            resize = image.resize((100,100)) 
            resize.load()
            data = np.asarray(resize, dtype="uint8")   
            if len(data.shape) == 3:
                data = data[:,:,0]
            data_4D = data.reshape(1,100,100,1) 
            pr = model.predict_classes(data_4D)[0]
            if (int_to_res[pr] != v):
                np.set_printoptions(threshold=np.nan)
                numWrong += 1
                print(data)
                wrongVals.append((v, int_to_res[pr]))
                plt.imshow(resize, cmap=cm.Greys_r) 
                plt.show()
                
        print("Number of wrong guesses:")
        print(numWrong)
        print("Wrong predictions are:")
        print(wrongVals)




# if __name__ == "__main__":
#     (x_train, y_train) = load_data()
#     x_train = np.asarray(x_train)

#     # Create label dictionary
#     res_to_int = {}
#     int_to_res = {}
#     counter = 0
#     for c in y_train:
#         if c not in res_to_int.keys():
#             # print(c)
#             # print(counter)
#             res_to_int[c] = counter
#             int_to_res[counter] = c
#             counter += 1

#     try:
#         model = load_model('new_model.h5')
#     except:
#         print('Training...')
#         model = train(x_train, y_train, res_to_int)
#         model.save('new_model.h5')
    
#     # image = Image.open("4plus2_2.jpg")
#     # image = Image.open("2plus3minus1.jpg")
#     # image = Image.open("2plus2.jpg")
#     image = Image.open("TestSet/6_1.jpg")
#     resize = image.resize((100,100))
#     data = np.asarray(image, dtype="uint8")
#     if len(data.shape) == 3: # make grayscale
#         data = data[:,:,0]
    
#     columns = []
#     for i in range(0, len(data[0])):
#         columns.append(column(data, i))
    

#     #columns = get_columns(data)

#     symbols = []
#     symbol = []



#     for column in columns:
#         if is_whitespace(column):
#             if symbol:  
#                 symbols.append(symbol)
#                 symbol = []
#         else:
#             symbol = append_column(symbol, column)
#     if symbol:
#         symbols.append(symbol)
    
#     print(len(symbols))

#     symbols = [squarify(symbol) for symbol in symbols]

#     operators = ['+', '-', '*', '/']

#     operandQueue = deque()
#     operatorQueue = deque()

#     for sym in symbols:
#         npsym = np.array(sym)
#         img = PIL.Image.fromarray(npsym.astype("uint8"))
#         image = PIL.ImageOps.invert(img)
#         resize = image.resize((100,100))
#         plt.imshow(resize, cmap=cm.Greys_r)
#         plt.show()      
#         resize.load()
#         data = np.asarray(resize, dtype="uint8")
#         data_4D = data.reshape(1,100,100,1)
#         pr = model.predict_classes(data_4D)[0]
#         result = int_to_res[pr]
#         print(result)
#         if is_operator(operators, result):
#             operatorQueue.append(result)
#         else:
#             try:
#                 operandQueue.append(int(result))
#             except:
#                 continue
    
#     if len(operatorQueue) < len(operandQueue):
#         print(operatorQueue)
#         print(operandQueue)
#         print('Result: ' + str(evaluate_expression(operandQueue, operatorQueue)))
#     else:
#         print('That is not a valid mathematical expression. Try again!')

