import os
    
path ="./TrainingSet2"
MAX_SIZE = 3000

for folder in os.listdir(path):
    counter = 0
    print(folder)
    for img in os.listdir(path + "/" + folder):
        if counter > MAX_SIZE:
            imgPath = path + "/" + folder + "/" + img
            os.unlink(imgPath)
            counter += 1
        counter += 1
