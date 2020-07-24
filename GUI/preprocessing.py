import numpy as np
import cv2 as cv
import os
from PIL import Image
class preprocessing:
    def __init__(self, axial_path, coronal_path, sagittal_path):
        axial_path = axial_path[1:-1]
        coronal_path = coronal_path[1:-1]
        sagittal_path = sagittal_path[1:-1]
        axial_images = axial_path.split(',')
        coronal_images = coronal_path.split(',')
        sagittal_images = sagittal_path.split(',')
        self.to_numpy(axial_images, 'axial.npy')
        self.to_numpy(coronal_images, 'coronal.npy')
        self.to_numpy(sagittal_images, 'sagittal.npy')
        return

    def to_numpy(self, images, file_name):
        if not os.path.exists('temp'):
            os.mkdir('temp')
        result = []
        for i in images:
            i = i.strip()
            i = i[1:-1]
            print(i)
            temp = cv.imread(i)
            temp = denoise_image(temp)
            img = self.resize_image(temp)
            data = np.array(img, dtype='uint8')
            result.append(data[:,:,0])
        np.save(r'temp/{}'.format(file_name), result)
        return
        
    def resize_image(self, img):
        pixles = 256
        if img.shape[0] > pixles or img.shape[1] > pixles:
            output = cv.resize(img, (pixles,pixles), interpolation=cv.INTER_CUBIC)
        else:
            output = cv.resize(img, (pixles,pixles), interpolation=cv.INTER_LINEAR)
        return output

    def denoise_image(self, image):
        gray = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
        _,edge = cv.threshold(gray,30,255,cv.THRESH_BINARY)
        contours,_ = cv.findContours(edge,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours,key=cv.contourArea,reverse=True)[0]
        mask = np.zeros(image.shape[:2],np.uint8)
        mask = cv.drawContours(mask,[contours],-1,(255),-1)
        res = cv.bitwise_and(image,image,mask=mask)
        return res
