from PyQt5.QtCore import *
from preprocessing import preprocessing
from models import Model
from database import DB
from shutil import copyfile
import sqlite3 as sq
import time

class ExamineSignals(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    

class ExamineThread(QRunnable):
    
    def __init__(self, get_data,  
                 axial_images, coronal_images, sagittal_images,
                 name, age, blood, note, time):
        super(ExamineThread, self).__init__()
        self.signals = ExamineSignals()
        self.get_data = get_data
        self.examine_result_abnormal = 0
        self.examine_result_acl = 0
        self.examine_result_men = 0
        self.axial_images = axial_images
        self.coronal_images = coronal_images
        self.sagittal_images = sagittal_images
        self.name = name
        self.age = age
        self.blood = blood
        self.note = note
        self.time = time
        
        self.db = DB()
        

    def get_text_result(self, result):
        if round(float(result)) == 0:
            return 'negative'
        else:
            return 'positive'
        
    def save_to_database(self):
        try:
            id = self.db.get_last_id()
        except Exception:
            id = 0
        finally:
            id += 1
        
        axial_path = r'database\axial_{}.npy'.format(id)
        coronal_path = r'database\coronal_{}.npy'.format(id)
        sagittal_path = r'database\sagittal_{}.npy'.format(id)
        
        copyfile(r'temp\axial.npy', axial_path)
        copyfile(r'temp\coronal.npy', coronal_path)
        copyfile(r'temp\sagittal.npy', sagittal_path)
        
        self.db.insert(id = id, 
                        name = self.name, 
                        age = self.age, 
                        blood = self.blood, 
                        axial = axial_path,
                        coronal=coronal_path, 
                        sagittal=sagittal_path, 
                        abnormal=self.examine_result_abnormal, 
                        acl=self.examine_result_acl,
                        men = self.examine_result_men, 
                        note=str(self.note),
                        time=self.time)
        self.db.close()
        
        
    def run(self):
        preprocessing(self.axial_images, self.coronal_images, self.sagittal_images)
        self.examine_result_abnormal = Model(key = 'abnormal').get_prediction()
        self.examine_result_acl = Model(key = 'acl').get_prediction()
        self.examine_result_men = Model(key = 'men').get_prediction()
        
        self.get_data(self.examine_result_abnormal,
                      self.examine_result_acl,
                      self.examine_result_men)
        
        self.save_to_database()
        self.db.close()
        
        # self.on_thread_finished()
        self.signals.finished.emit()
        
        return