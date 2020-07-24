from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
import os
import sys
from preprocessing import Model as pre_Model
from design import Ui_MainWindow
from abnormal import Model
from database import DB
from shutil import copyfile
from exports import Exports
import xlsxwriter as xls
import glob

MainUI, _ = loadUiType('untitled.ui')


class MainApp(QMainWindow, MainUI):  # Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handle_ui()
        self.handle_buttons()
        self.handle_action_bar()
        self.db = ''
        self.handle_database()
        return

    def handle_database(self):
        # try: self.db = DB(False)
        # except Exception: self.db = DB(True)

        # try: self.db.create_database()
        # except Exception: ''

        # try: self.db.create_table()
        # except Exception: ''
        self.db = DB()

    def handle_ui(self):
        self.setWindowTitle('MRI scanner')
        self.setFixedSize(850, 500)
        self.report.setEnabled(False)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(99)
        return

    def handle_buttons(self):
        self.browseAxial.clicked.connect(lambda x: self.getLocation(0))
        self.browseCoronal.clicked.connect(lambda x: self.getLocation(1))
        self.browseSagittal.clicked.connect(lambda x: self.getLocation(2))
        self.submit.clicked.connect(self.processing)

    def handle_action_bar(self):
        # self.actionstate_info.triggered.connect(self.extract_video)
        self.actionwith_2_frames.triggered.connect(lambda x: self.extract_video(2))
        self.actionwith_4_frames.triggered.connect(lambda x: self.extract_video(4))
        self.actionwith_8_frames.triggered.connect(lambda x: self.extract_video(8))
        self.actionwith_15_frames.triggered.connect(lambda x: self.extract_video(15))
        self.actionwith_30_frames.triggered.connect(lambda x: self.extract_video(30))

        self.actiondelete_all_data.triggered.connect(self.delete_all_data)

        self.actionexcel_sheet.triggered.connect(self.extract_xlsx)

    def delete_all_data(self):
        self.db.trunc()
        for i in glob.glob('data/*.npy'):
            os.remove(i)
        for i in glob.glob('database/*.npy'):
            os.remove(i)

    def extract_xlsx(self):
        try:
            loc = QFileDialog.getSaveFileName(
                self, 'Choose File', directory=os.path.dirname(__file__))
        except FileNotFoundError:
            QMessageBox.warning(self, "Error!", "can\'t find path")
        loc = str(loc[0])[:]
        os.mkdir(loc)

        workbook = xls.Workbook(os.path.join(loc, 'data.xlsx'))
        worksheet = workbook.add_worksheet()

        rows = self.db.get_all_data()
        worksheet.write(0, 0, 'ID')
        worksheet.write(0, 1, 'Name')
        worksheet.write(0, 2, 'Age')
        worksheet.write(0, 3, 'Axial directory')
        worksheet.write(0, 4, 'coronal directory')
        worksheet.write(0, 5, 'sagittal directory')
        worksheet.write(0, 6, 'result')

        for i, row in enumerate(rows):
            for col in range(0, 8):
                worksheet.write(i + 1, col, row[col])

        workbook.close()
        return

    def extract_video(self, frames):
        try:
            loc = QFileDialog.getSaveFileName(
                self, 'Choose File', directory=os.path.dirname(__file__))
        except FileNotFoundError:
            QMessageBox.warning(self, "Error!", "can\'t find path")
        loc = str(loc[0])[:]

        os.mkdir(loc)
        target_id = self.db.get_last_id()
        about = 'Name : {} \nAge : {}\nresult : {}\ncreated at : {}'.format(
            self.db.get_name(target_id), self.db.get_age(target_id),
            self.get_text_result(self.db.get_result(target_id)),
            self.db.get_created_on(target_id))
        f = open(os.path.join(loc, 'data.txt'), 'w')
        f.write(about)
        f.close()

        Exports.export_video('axial', frames, 'axial', loc)
        Exports.export_video('coronal', frames, 'coronal', loc)
        Exports.export_video('sagittal', frames, 'sagittal', loc)

    def getLocation(self, key):
        loc = QFileDialog.getOpenFileNames(self,
                                           'Open File', directory=os.path.dirname(__file__),
                                           filter='Image (*.jpg *.JPG *.png *.PNG *.jpeg *.JPEG)')
        loc = str(loc[0])[:]
        if key == 0:
            self.axialText.setText(loc)
        elif key == 1:
            self.coronalText.setText(loc)
        else:
            self.sagittalText.setText(loc)

    def processing(self):
        try:
            pre_Model(self.axialText.toPlainText()
                      , self.coronalText.toPlainText()
                      , self.sagittalText.toPlainText())
            self.report.setEnabled(True)
        except Exception:
            QMessageBox.warning(self, "Error!", "can\'t upload images")
        else:
            examine_result = Model().get_prediction()
            # start_progress_bar()
            QApplication.processEvents()
            self.send_data_to_db(examine_result)
            examine_result = self.get_text_result(examine_result)
            report = 'Report: \nresult is {}'.format(examine_result)

            self.report.setPlainText(report)

    def send_data_to_db(self, examine_result):
        name = self.axialText_3.toPlainText()
        if name == '' or name == None:
            name = 'no name'
        age = self.spinBox.value()
        last_id = self.db.get_last_id() + 1

        copyfile('data/axial.npy', 'database/{}_axial.npy'.format(last_id))
        copyfile('data/coronal.npy', 'database/{}_coronal.npy'.format(last_id))
        copyfile('data/sagittal.npy', 'database/{}_sagittal.npy'.format(last_id))

        axial_dir = r'database/{}_axial.npy'.format(last_id)
        coronal_dir = r'database/{}_coronal.npy'.format(last_id)
        sagittal_dir = r'database/{}_sagittal.npy'.format(last_id)

        self.db.insert(name, str(age), axial_dir, coronal_dir, sagittal_dir, examine_result)

    def get_text_result(self, result):
        if round(float(result)) == 0:
            return 'negative'
        else:
            return 'positive'


app = QApplication(sys.argv)
window = MainApp()
window.show()
app.exec_()
