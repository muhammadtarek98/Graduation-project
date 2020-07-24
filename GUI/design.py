from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from PyQt5.QtCore import QThreadPool, QRunnable, Qt, pyqtSlot
import os
import sys
from database import DB
from shutil import copyfile
from preprocessing import preprocessing
import sqlite3 as sq
#from design import Ui_MainWindow
#from abnormal import Model
#from database import DB
#from shutill import copyfile
from exports import Exports
import xlsxwriter as xls
import glob
import threads
import time
from DateTime import DateTime
import numpy as np
import cv2 as cv

from PyQt5 import uic
from PyQt5.QtGui import QPixmap

MainUI, _ = loadUiType(r'GUI\main4.ui')

class MainApp(QMainWindow, MainUI):
    
    def __init__(self,parent= None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        # self.MainWindow.setFixedWidth(965)
        # self.MainWindow.setFixedHeight(565)
        
        self.db = DB()
        
        self.handle_buttons()
        self.tabWidget.setCurrentIndex(0)
        self.handle_table_tab()
        
        self.threadpool = QThreadPool()
        self.examine_result = 0
        self.abnormal, self.acl, self.men = 0,0,0
        self.dialog = None
        self.extract_dialog = None
        
        self.txt_search.textChanged.connect(self.filter_)
        
        # pix = QPixmap('motor.jpg')
        # pix.scaledToWidth(40)
        # pix.scaledToHeight(40)
        # a2 = QLabel()
        # a2.setMaximumWidth(40)
        # a2.setMaximumHeight(40)
        # a2.setPixmap(pix)
        # # a2.hide()
        
        return
    
    def StartDialog(self, id, name, age, blood, note):
        self.dialog = uic.loadUi(r"GUI\dialog.ui")
        self.dialog.txt_id.setPlainText(id)
        self.dialog.txt_name.setPlainText(name)
        self.dialog.spin_age.setValue(age)
        self.dialog.combo_blood.setCurrentIndex(blood)
        self.dialog.txt_note.setPlainText(note)
        self.dialog.bu_update.clicked.connect(lambda x: self.dialog_update(id))
        self.dialog.bu_delete.clicked.connect(lambda x: self.dialog_delete(id))
        self.dialog.bu_extract.clicked.connect(lambda x: self.dialog_extract(id))
        self.dialog.show()
        
    @pyqtSlot()
    def dialog_update(self, id):
        self.db.update_name(id, self.dialog.txt_name.toPlainText())
        self.db.update_age(id, self.dialog.spin_age.value())
        self.db.update_blood(id, self.dialog.combo_blood.currentIndex())
        self.db.update_note(id, self.dialog.txt_note.toPlainText())
        self.dialog_close()
        self.lbl_state.setText('state with id:{} successfully updated!'.format(id))
        
    @pyqtSlot()
    def dialog_delete(self, id):
        self.db.delete(id)
        self.dialog_close()
        self.lbl_state.setText('state with id:{} successfully deleted!'.format(id))
    
    def dialog_close(self):
        self.update_table(self.db.get_all_data(50))
        self.dialog.reject()
        
    @pyqtSlot()
    def dialog_extract(self, id):
        self.start_dialog_extract(id)
        self.dialog_close()
        
    def start_dialog_extract(self, id):
        self.extract_dialog = uic.loadUi(r'GUI\extract.ui')
        self.extract_dialog.bu_save.clicked.connect(lambda x:self.get_save_location(id))
        self.extract_dialog.check_video.stateChanged.connect(self.video_check_changed)
        self.extract_dialog.show()
        
    @pyqtSlot()
    def video_check_changed(self, state):
        if state == 2:
            self.extract_dialog.combo_video.setEnabled(True)
        else:
            self.extract_dialog.combo_video.setEnabled(False)
            
    @pyqtSlot()
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
        #self.tableWidget.setTextAlignment(Qt.AlignHCenter)
    
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
            self.tableWidget.item(i,0).setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.item(i,1).setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.item(i,2).setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.item(i,3).setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.item(i,4).setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.item(i,5).setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.item(i,6).setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.item(i,7).setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.item(i,8).setTextAlignment(Qt.AlignHCenter)
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
        
    def cell_clicked(self, row, column):
        id = self.tableWidget.item(row,0).text()
        print('clicked id : ', id)
        self.StartDialog(id,
                         self.db.get_name(id), 
                         self.db.get_age(id),
                         self.db.get_blood(id),
                         self.db.get_note(id))

    # def cell_clicked(self, row, column):
    #     self.tabWidget.setCurrentIndex(2)
    #     id = self.tableWidget.item(row,0).text()
    #     self.txt_id_edit.setPlainText(self.db.get_name(id))
    #     self.spin_age_edit.setValue(self.db.get_age(id))
    #     self.combo_blood_edit.setCurrentIndex(self.db.get_blood(id))
    #     self.txt_note_edit.setPlainText(self.db.get_note(id))
    #     return
        
    @pyqtSlot()
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
        
    @pyqtSlot()
    def examine(self):
        now = DateTime()
        try:
            preprocessing(self.axial_images_location, 
                          self.coronal_images_location, 
                          self.sagittal_images_location)
        except AttributeError:
            QMessageBox.warning(self, "Error!", "can\'t load images!")
            return
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
        abnormal    : {}
        acl         : {}
        menalusis   : {}
        '''.format(
            self.get_text_result(self.abnormal), 
            self.get_text_result(self.acl),
            self.get_text_result(self.men))
        self.txt_report.setPlainText(report)
        self.lbl_state.setText('Done, state saved successfully!')
        
    @pyqtSlot()
    def get_images(self, key):
        #directory=os.path.dirname(__file__)
        loc = QFileDialog.getOpenFileNames(self,
                'Open File', 
                directory = os.path.join(os.environ["HOMEPATH"], "Desktop"), 
                filter='Image (*.jpg *.JPG *.png *.PNG *.jpeg *.JPEG)')
        print('-----------loc : ', loc)
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
        
    @pyqtSlot()
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
    
            
app = QApplication(sys.argv)
window = MainApp()
window.show()
app.exec_()