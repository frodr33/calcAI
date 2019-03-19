import numpy as np
import cv2
from PIL import Image
from PIL import ImageMath
import PIL.ImageOps


def column_average(column):
    return np.average(column)

def column_search(column):
    if column_average(column) < 240:
        return True
    return False

def f_number_snip(img):
    sep = []
    img_detec = 0
    for column in range(len(img)):
        column_added = 0
        if (column_added == 0):
            if (img_detec == 1):
                if (column_search(img[column])):
                    print(column_average(img[column]))
                    sep.append(img[column])
                    column_added +=1
                else:
                    return sep
                    img_detec == 0

            elif (img_detec == 0 and column_search(img[column])):
                    sep.append(img[column])
                    column_added +=1
                    img_detec +=1

if __name__ == "__main__":
    image = Image.open("5_2.JPG")
    image = PIL.ImageOps.invert(image)
    res = np.asarray(image, dtype="uint8")
    print(res[])
