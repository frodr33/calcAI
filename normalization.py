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

# def handleRemoveReadonly(func, path, exc):
#   excvalue = exc[1]
#   if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
#       os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
#       func(path)
#   else:
#       raise

# shutil.rmtree(filename, ignore_errors=False, onerror=handleRemoveReadonly)