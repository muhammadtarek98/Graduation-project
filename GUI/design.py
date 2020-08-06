from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from PyQt5.QtCore import QThreadPool, QRunnable, Qt, pyqtSlot
import os
import sys
from database import DB
from shutil import copyfile
from preprocessing import preprocessing
import sqlite3 as sq
from exports import Exports
import xlsxwriter as xls
import glob
import threads
import time
from DateTime import DateTime
import numpy as np
import cv2 as cv
import re

from PyQt5 import uic
from PyQt5.QtGui import QPixmap

#from GUI.main import Ui_MainWindow as main_gui
#from GUI.dialog import Ui_Dialog as dialog_gui
#from GUI.extract import Ui_Dialog as extract_gui

MainUI, _ = loadUiType(r'GUI\main.ui')

class MainApp(QMainWindow, MainUI):
    
    def __init__(self,parent= None):
        super(MainApp, self).__init__(parent)
        self.setupUi(self)
        
        self.setFixedWidth(965)
        self.setFixedHeight(585)
        
        self.db = DB()
        
        self.handle_buttons()
        self.handle_table_tab()
        
        self.threadpool = QThreadPool()
        self.abnormal, self.acl, self.men = 0,0,0
        self.edit_dialog = None
        self.extract_dialog = None
        return
    
    def start_edit_dialog(self, id, name, age, blood, note):
        self.edit_dialog = uic.loadUi(r"GUI\edit_dialog.ui")
        self.edit_dialog.txt_id.setPlainText(id)
        self.edit_dialog.txt_name.setPlainText(name)
        self.edit_dialog.spin_age.setValue(age)
        self.edit_dialog.combo_blood.setCurrentIndex(blood)
        self.edit_dialog.txt_note.setPlainText(note)
        self.edit_dialog.bu_update.clicked.connect(lambda x: self.edit_dialog_update(id))
        self.edit_dialog.bu_delete.clicked.connect(lambda x: self.edit_dialog_delete(id))
        self.edit_dialog.bu_extract.clicked.connect(lambda x: self.dialog_extract(id))
        self.edit_dialog.show()
        
    def edit_dialog_update(self, id):
        self.db.update_name(id, self.edit_dialog.txt_name.toPlainText())
        self.db.update_age(id, self.edit_dialog.spin_age.value())
        self.db.update_blood(id, self.edit_dialog.combo_blood.currentIndex())
        self.db.update_note(id, self.edit_dialog.txt_note.toPlainText())
        self.edit_dialog_close()
        self.lbl_state.setText('state with id:{} successfully updated!'.format(id))
        
    def edit_dialog_delete(self, id):
        self.db.delete(id)
        self.edit_dialog_close()
        self.lbl_state.setText('state with id:{} successfully deleted!'.format(id))
    
    def edit_dialog_close(self):
        self.update_table(self.db.get_all_data(50))
        self.edit_dialog.reject()
        
    def dialog_extract(self, id):
        self.start_dialog_extract(id)
        self.edit_dialog_close()
        
    def start_dialog_extract(self, id):
        self.extract_dialog = uic.loadUi(r'GUI\extract.ui')
        self.extract_dialog.bu_save.clicked.connect(lambda x:self.get_save_location(id))
        self.extract_dialog.check_video.stateChanged.connect(self.video_check_changed)
        self.extract_dialog.show()
        
    def video_check_changed(self, state):
        if state == 2:
            self.extract_dialog.combo_video.setEnabled(True)
        else:
            self.extract_dialog.combo_video.setEnabled(False)
            
    def get_save_location(self, id):
        loc = QFileDialog.getSaveFileName(self,
                'Open File', 
                directory = os.path.join(os.environ["HOMEPATH"], "Desktop"), 
                filter='All Files (*)')
        loc = str(loc[0])
        if loc == '':
            loc = os.path.join(os.environ["HOMEPATH"], r"Desktop\{}".format(id))
        if not os.path.exists(loc):
            os.mkdir(loc)
        if self.extract_dialog.check_personal.isChecked():
            file = open(loc + r'\data.txt', 'w')
            file.write(
                '''
                ID    :\t{}
                Name  :\t{}
                Age   :\t{}
                Blood :\t{}
                Note  :\t{}
                Acl      result :\t{}
                Abnormal result :\t{}
                Men      result :\t{}
                '''.format(id, 
                            self.db.get_name(id),
                            self.db.get_age(id),
                            self.get_text_blood(self.db.get_blood(id)),
                            self.db.get_note(id),
                            self.get_text_result(self.db.get_acl(id)),
                            self.get_text_result(self.db.get_abnormal(id)),
                            self.get_text_result(self.db.get_men(id))))
    
        if self.extract_dialog.check_images.isChecked():
            self.extract_images(id, loc)
        if self.extract_dialog.check_video.isChecked():
            frames = self.extract_dialog.combo_video.currentIndex()
            if frames == 0: frames = 30
            elif frames == 1: frames = 15
            elif frames == 2: frames = 30
            elif frames == 3: frames = 60
            self.extract_video(id, loc, frames)
        self.lbl_state.setText('state with id:{}, Data successfully extracted!'.format(id))
        
        self.extract_dialog.reject()
    
    def handle_table_tab(self):
        self.tableWidget.setColumnWidth(0,10)
        self.tableWidget.setColumnWidth(1,200)
        self.tableWidget.setColumnWidth(2,20)
        self.tableWidget.setColumnWidth(3,20)
        self.tableWidget.setColumnWidth(4,70)
        self.tableWidget.setColumnWidth(5,70)
        self.tableWidget.setColumnWidth(6,70)
        self.tableWidget.setColumnWidth(7,300)
        self.tableWidget.setColumnWidth(8,130)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.txt_search.textChanged.connect(self.filter_)
    
    def update_table(self, data):
        if self.tabWidget.currentIndex() != 1: return
        self.tableWidget.setRowCount(len(data))
        for i in range(0, len(data)):
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(data[i][0])))#id
            self.tableWidget.setItem(i,1, QTableWidgetItem(str(data[i][1])))#name
            self.tableWidget.setItem(i,2, QTableWidgetItem(str(data[i][2])))#age
            self.tableWidget.setItem(i,3, QTableWidgetItem(self.get_text_blood(data[i][3])))#blood
            self.tableWidget.setItem(i,4, QTableWidgetItem(self.get_text_result(data[i][7])))#abnormal
            self.tableWidget.setItem(i,5, QTableWidgetItem(self.get_text_result(data[i][8])))#acl
            self.tableWidget.setItem(i,6, QTableWidgetItem(self.get_text_result(data[i][9])))#men
            self.tableWidget.setItem(i,7, QTableWidgetItem(str(data[i][10])))#note
            self.tableWidget.setItem(i,8, QTableWidgetItem(str(data[i][11])))#created at
            for j in range(0,9):
                self.tableWidget.item(i,j).setTextAlignment(Qt.AlignHCenter)
        self.lbl_state.setText('table successfully updated!')
        return
        
    
    def handle_buttons(self):
        self.btn_axial.clicked.connect(lambda x: self.get_images(0))
        self.btn_coronal.clicked.connect(lambda x: self.get_images(1))
        self.btn_sagittal.clicked.connect(lambda x: self.get_images(2))
        self.btn_examine.clicked.connect(self.examine)
        self.tabWidget.currentChanged.connect(lambda x: self.update_table(
            self.db.get_all_data(50)))
        self.tabWidget.setTabEnabled(2, False)
        
        self.tableWidget.cellDoubleClicked.connect(self.cell_clicked)
        self.menu_excel_file.triggered.connect(self.extract_xlsx)
        self.tabWidget.setCurrentIndex(0)
        
    def cell_clicked(self, row, column):
        id = self.tableWidget.item(row,0).text()
        self.start_edit_dialog(id,
                         self.db.get_name(id), 
                         self.db.get_age(id),
                         self.db.get_blood(id),
                         self.db.get_note(id))
    
    def filter_(self):
        engine = self.txt_search.toPlainText()
        if self.radio_id.isChecked() == True: 
            if engine == '':
                data = self.db.filter_by_name('')
            elif engine.isdigit(): data = self.db.filter_by_id(engine)
            else: data = self.db.filter_by_id('-1')
        elif self.radio_name.isChecked() == True: 
            data = self.db.filter_by_name(engine)
        else:
            data = self.db.filter_by_Date(engine)
        
        self.update_table(data)
        return
        
    
    def examine(self):
        now = DateTime()

        if self.axial_images_location == '[]'or self.coronal_images_location == '[]'or self.sagittal_images_location == '[]':
            QMessageBox.warning(self, "Error!", "can\'t load images!")
            return

        if not self.check_text_constrains(self.get_name()):
            QMessageBox.warning(self, "Error!", "name field can't contain (' , \)")
            return

        if not self.check_text_constrains(self.get_note()):
            QMessageBox.warning(self, "Error!", "note field can't contain (' , \)")
            return
        self.btn_examine.setEnabled(False)
        self.lbl_state.setText('in progress...')
        self.th = threads.ExamineThread(
            self.get_thread_data, 
            self.axial_images_location,
            self.coronal_images_location,
            self.sagittal_images_location,
            self.get_name(),
            self.get_age(),
            self.get_blood(),
            self.get_note(),
            now.Date() + ' ' + now.AMPM())
        self.th.signals.finished.connect(self.on_thread_finished)
        self.threadpool.start(self.th)
        
    
    def get_thread_data(self, abnormal, acl, men):
        self.abnormal = abnormal
        self.acl = acl
        self.men = men
    
    def on_thread_finished(self):
        report = '''
        Abnormal\t: {}
        Acl\t\t: {}
        Meniscus\t: {}
        '''.format(
            self.get_text_result(self.abnormal), 
            self.get_text_result(self.acl),
            self.get_text_result(self.men))
        self.txt_report.setPlainText(report)
        self.lbl_state.setText('Done, state saved successfully!')
        self.btn_examine.setEnabled(True)
        self.reset_fieldes()
        
    def get_images(self, key):
        
        loc = QFileDialog.getOpenFileNames(self,
                'Open File', directory =
                os.path.join(os.environ["HOMEPATH"], "Desktop"),
                filter='Image (*.jpg *.JPG *.png *.PNG *.jpeg *.JPEG)')
        loc = str(loc[0])[:]
        num_images = len(loc.split(','))
        if key == 0: 
            self.axial_images_location = loc
            if loc == '[]': self.lbl_axial_counter.setText('no image selected')
            else: self.lbl_axial_counter.setText('{} images selected'.format(num_images))
        elif key == 1: 
            self.coronal_images_location = loc
            if loc == '[]': self.lbl_coronal_counter.setText('no image selected')
            else: self.lbl_coronal_counter.setText('{} images selected'.format(num_images))
        else : 
            self.sagittal_images_location = loc
            if loc == '[]': self.lbl_sagittal_counter.setText('no image selected')
            else: self.lbl_sagittal_counter.setText('{} images selected'.format(num_images))
        return
        
    def get_name(self):
        self.name = self.txt_name.toPlainText()
        return self.name
    
    def get_blood(self):
        self.blood = self.combo_blood.currentIndex()
        return self.blood
        
    def get_age(self):
        self.age = self.spin_age.value()
        return self.age
    
    def get_note(self):
        self.note = self.txt_note.toPlainText()
        return self.note
    
    def get_text_result(self, result):
        if round(float(result)) == 0:
            return 'negative'
        else:
            return 'positive'
        
    def get_text_blood(self, blood):
        if blood == 0: return 'None'
        return 'A+ A- B+ B- AB+ AB- O+ O-'.split()[blood-1]
    
    def extract_video(self, id, loc, frames):
        Exports.export_video(id, 'axial', frames, 'axial', loc)
        Exports.export_video(id, 'coronal', frames, 'coronal', loc)
        Exports.export_video(id, 'sagittal', frames, 'sagittal', loc)
        
    def extract_xlsx(self):
        try:
            loc = QFileDialog.getSaveFileName(
                self, 'Choose File', directory = os.path.dirname(__file__))
        except FileNotFoundError: 
            QMessageBox.warning(self, "Error!", "can\'t find path")
        loc = str(loc[0])[:]
        if loc == '': return
        os.mkdir(loc)
        
        worksheet = workbook.add_worksheet()
        rows = self.db.get_all_data()
        worksheet.write(0, 0, 'ID')
        worksheet.write(0, 1, 'Name')
        worksheet.write(0, 2, 'Age')
        worksheet.write(0, 3, 'Blood')
        worksheet.write(0, 4, 'Abnormal result')
        worksheet.write(0, 5, 'Acl result')
        worksheet.write(0, 6, 'Men result')
        worksheet.write(0, 7, 'Note')
        worksheet.write(0, 8, 'Created at')
        
        for i,row in enumerate(rows):
            worksheet.write(i, 0, row[0])#id
            worksheet.write(i, 1, row[1])#name
            worksheet.write(i, 2, row[2])#age
            worksheet.write(i, 3, self.get_text_blood(row[3]))#blood
            worksheet.write(i, 4, self.get_text_result(row[7]))#abnormal
            worksheet.write(i, 5, self.get_text_result(row[8]))#acl
            worksheet.write(i, 6, self.get_text_result(row[9]))#men
            worksheet.write(i, 7, row[10])#note
            worksheet.write(i, 8, row[11])#time
            
        workbook.close()   
        self.lbl_state.setText('all data successfully extracted!')
        return
    
    def extract_images(self, id, location):
        if location == '':
            location = os.path.join(os.environ["HOMEPATH"], r"Desktop\{}".format(id))
        axial = np.load(r'database\axial_{}.npy'.format(id))
        coronal = np.load(r'database\coronal_{}.npy'.format(id))
        sagittal = np.load(r'database\sagittal_{}.npy'.format(id))
        os.mkdir(os.path.join(location, 'axial images'))
        os.mkdir(os.path.join(location, 'coronal images'))
        os.mkdir(os.path.join(location, 'sagittal images'))
        for j,i in enumerate(axial):
            cv.imwrite(os.path.join(location, 'axial images') + r'\{}.jpg'.format(j), i)
        for j,i in enumerate(coronal):
            cv.imwrite(os.path.join(location, 'coronal images') + r'\{}.jpg'.format(j), i)
        for j,i in enumerate(sagittal):
            cv.imwrite(os.path.join(location, 'sagittal images') + r'\{}.jpg'.format(j), i)

    def check_text_constrains(self, text):
        text = re.search(r"'|\\|\"", text)
        if text: return False
        return True

    def reset_fieldes(self):
        self.txt_name.setPlainText('')
        self.combo_blood.setCurrentIndex(0)
        self.spin_age.setValue(0)
        self.txt_note.setPlainText('')
        self.axial_images_location = '[]'
        self.sagittal_images_location = '[]'
        self.coronal_images_location = '[]'
    
            
app = QApplication(sys.argv)
window = MainApp()
window.show()
app.exec_()
