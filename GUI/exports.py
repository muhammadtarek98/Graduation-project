#convert .npy to video > axial,coronal,sagittal
#PDF report with images, name, id, result, date
#excel sheet with all states
import cv2 as cv
import numpy as np
import os
        
class Exports:
    
    @staticmethod
    def export_video(id, export_type, num_frames, file_name, save_location = 'BASE'):
        if export_type not in ['axial', 'coronal', 'sagittal']:
            export_type = 'axial'
        if num_frames > 60 or num_frames <0:
            num_frames = 30
        try:
            images_npy = np.load(r'database\{}_{}.npy'.format(export_type,id))
        except Exception:
            raise FileNotFoundError('can\'t find data/{}.npy!'.format(export_type))
        images = []
        for i in images_npy:
            cv.imwrite(r'data/temp.jpg', i)
            images.append(cv.imread(r'data/temp.jpg'))
        os.remove(r'data/temp.jpg')
        if save_location == 'BASE':
            video = cv.VideoWriter('{}/{}.mp4'.format(file_name), cv.VideoWriter_fourcc(*'MP4V'), num_frames, (256,256))
        else:
            video = cv.VideoWriter('{}/{}.mp4'.format(save_location, file_name), cv.VideoWriter_fourcc(*'MP4V'), num_frames, (256,256))
        for i in images:
            video.write(i)
        video.release()
        cv.destroyAllWindows()
        
    
