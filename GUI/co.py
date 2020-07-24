import cv2 as cv
import numpy as np
import os
from pathlib import Path


def start(arr,path):
    img = np.load(arr, allow_pickle=True)
    k = 0
    for i in img:
        file = str(k) + ".png"
        cv.imwrite(path+file, i)
        k+=1

start("axial/0000.npy","axial/")
start('coro/0000.npy',"coro/")
start("sagittal/0000.npy","sagittal/")
