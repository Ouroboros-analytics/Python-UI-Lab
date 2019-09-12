from PyQt5 import QtWidgets
from ui import Ui_MainWindow
import sys
from pathlib import Path
from PyQt5.QtGui import QKeySequence, QPalette, QColor
from PyQt5.QtCore import Qt
import json


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        set_path = Path('settings.json')
        with set_path.open() as settings_file:
            settings = json.load(settings_file)
            print(settings)
            if settings['lessonPath'] == 'null':
                les_path_sel = QtWidgets.QTreeView()
                les_path_sel.setWindowTitle('Select Lesson Plans Directory')

        lessons = Path(
            '~/Documents/DataViz-Lesson-Plans/01-Lesson-Plans').expanduser()
        lessons_dirs = [x for x in lessons.iterdir() if x.is_dir()]
        for lesson in lessons_dirs:
            self.ui.lessonList.addItem(lesson.stem)

        self.ui.activityList.les_dirs = lessons_dirs

        self.ui.radioButton.value = '1/Activities'
        self.ui.radioButton.setChecked(True)
        self.ui.radioButton.toggled.connect(self.radioClicked)
        self.ui.radioButton_2.value = '2/Activities'
        self.ui.radioButton_2.toggled.connect(self.radioClicked)
        self.ui.radioButton_3.value = '3/Activities'
        self.ui.radioButton_3.toggled.connect(self.radioClicked)

        self.ui.lessonList.currentIndexChanged.connect(self.radioClicked)

    def radioClicked(self):
        if self.ui.radioButton.isChecked():
            radioButton = self.ui.radioButton
        elif self.ui.radioButton_2.isChecked():
            radioButton = self.ui.radioButton_2
        elif self.ui.radioButton_3.isChecked():
            radioButton = self.ui.radioButton_3
        self.ui.activityList.cur_les = self.ui.lessonList.currentIndex()
        self.ui.activityList.cur_day = radioButton.value
        self.ui.activityList.clear()
        self.update_activity()

    def update_activity(self):
        activity_l = self.ui.activityList
        try:
            act_path = Path(
                activity_l.les_dirs[activity_l.cur_les]) / activity_l.cur_day
            activity_list = [x for x in act_path.iterdir() if x.is_dir()]
            for activity in activity_list:
                activity_l.addItem(activity.stem)
            activity_l.update()
        except FileNotFoundError:
            error = QtWidgets.QMessageBox()
            error.setText('File path does not exist')
            error.setWindowTitle('Error')
            error.setIcon(QtWidgets.QMessageBox.Critical)
            error.exec_()


app = QtWidgets.QApplication([])

# Force the style to be the same on all OSs:
app.setStyle("Fusion")

# Now use a palette to switch to dark colors:
# palette = QPalette()
# palette.setColor(QPalette.Window, QColor(53, 53, 53))
# palette.setColor(QPalette.WindowText, Qt.white)
# palette.setColor(QPalette.Base, QColor(25, 25, 25))
# palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
# palette.setColor(QPalette.ToolTipBase, Qt.white)
# palette.setColor(QPalette.ToolTipText, Qt.white)
# palette.setColor(QPalette.Text, Qt.white)
# palette.setColor(QPalette.Button, QColor(53, 53, 53))
# palette.setColor(QPalette.ButtonText, Qt.white)
# palette.setColor(QPalette.BrightText, Qt.red)
# palette.setColor(QPalette.Link, QColor(42, 130, 218))
# palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
# palette.setColor(QPalette.HighlightedText, Qt.black)
# app.setPalette(palette)

win = Window()
win.show()

sys.exit(app.exec())
