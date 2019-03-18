# import keras, io
# from keras.datasets import mnist
# from keras.models import Sequential
# from keras.layers import Dense, Dropout, Flatten
# from keras.layers import Conv2D, MaxPooling2D
import numpy as np
import cv2
from PIL import Image
from PIL import ImageMath

# from keras.models import load_model # creates a HDF5 file 'my_model.h5'
# from keras.datasets import mnist
# import keras
# import os
# import pickle
# import gzip
# import matplotlib.cm as cm
# import matplotlib.pyplot as plt
# import random
import PIL.ImageOps
# os.environ["TF_CPP_MIN_LOG_LEVEL"]="3"


def column_average(column):
    return np.average(column)

def column_search(column):
    if column_average(column) < 240:
        return True
    return False
    # for entry in range(len(column)):
    #     if (column[entry] < 230):
    #         return True
    # return False


def f_number_snip(img):
    sep = []
    img_detec = 0
    for column in range(len(img)):
        column_added = 0
        if (column_added == 0):
            # print(str(img_detec) + "" + str(column))
            if (img_detec == 1):
                if (column_search(img[column])):
                    print(column_average(img[column]))
                    sep.append(img[column])
                    # print(sep)
                    # print(len(sep))
                    column_added +=1
                else: # once it finds one entry not <240 set_printoptions
                    # print(sep)
                    # print(len(sep))
                    return sep
                    img_detec == 0

            elif (img_detec == 0 and column_search(img[column])):
                    sep.append(img[column])
                    # print("made first")
                    column_added +=1
                    img_detec +=1




if __name__ == "__main__":
    # image = Image.open("5.png")
    # resize = image.resize((,45))
    # res = np.asarray(resize, dtype="uint8")
    # fir_image = Image.fromarray(res.astype('uint8'), 'RGB')

    image = Image.open("5_2.JPG")
    image = PIL.ImageOps.invert(image)
    # resize = image.resize((45,45))
    # resize.load()
    res = np.asarray(image, dtype="uint8")
    print(res[])
    # for i in range(len(res)):
    # print(res[4])
    # # print(res)
    # # img = cv2.imread("5_2.JPG",0)
    # # res = cv2.resize(img, dsize=(45, 45), interpolation=cv2.INTER_CUBIC)
    # # print(res)
    # first_img_arr = np.array(f_number_snip(res))
    # print(first_img_arr)
    # print(column_average(first_img_arr))
    # fir_image = Image.fromarray(first_img_arr.astype('uint8'), 'RGB')
    # print(first_img)

                # sep = np.append(sep, img[column], axis =0)

    # I used my way above bc I needed to invert the images bc background
    # is 255 but to train better, a background value of 0 is needed
    # img = cv2.imread("TestSet/0_1.jpg",0)
    # res = cv2.resize(img, dsize=(28, 28), interpolation=cv2.INTER_CUBIC)
    # plt.imshow(res, cmap=cm.Greys_r)
    # plt.show()
    # batch = np.expand_dims(res,axis=0)
    # batch = np.expand_dims(batch,axis=3)
    # print(model.predict(batch))
    # print(model.predict_classes(batch))
