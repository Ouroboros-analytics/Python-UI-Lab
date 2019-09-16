from PyQt5 import QtWidgets
from ui import Ui_MainWindow
import sys
import subprocess
from pathlib import Path
from PyQt5.QtGui import QKeySequence, QPalette, QColor, QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt, pyqtSlot
import json
import shutil
import pprint

app = QtWidgets.QApplication([])


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.set_path = Path('settings.json')
        self.settings = json.load(self.set_path.open())
        lessons = Path(self.settings['lessonPath']
                       ).expanduser() / '01-Lesson-Plans'
        lessons_dirs = [x for x in lessons.iterdir() if x.is_dir()]
        for lesson in lessons_dirs:
            self.ui.lessonList.addItem(lesson.stem)

        self.ui.activityList.les_dirs = lessons_dirs

        self.ui.radioButton.value = '1'
        self.ui.radioButton.setChecked(True)
        self.ui.radioButton.toggled.connect(self.radioClicked)
        self.ui.radioButton_2.value = '2'
        self.ui.radioButton_2.toggled.connect(self.radioClicked)
        self.ui.radioButton_3.value = '3'
        self.ui.radioButton_3.toggled.connect(self.radioClicked)

        self.ui.lessonList.currentIndexChanged.connect(self.radioClicked)

        self.class_repo = Path(
            self.settings['classPath'], self.settings['classDay']).expanduser()
        print(self.class_repo)
        self.ui.activitiesDone.basePath = [
            x for x in self.class_repo.iterdir() if x.is_dir()]

        self.ui.pushActivity.clicked.connect(self.pushActivity)

        if self.settings['theme'] == 'light':
            self.ui.action_Dark_Mode.setChecked(False)
            self.light_mode()
        elif self.settings['theme'] == 'dark':
            self.ui.action_Dark_Mode.setChecked(True)
            self.dark_mode()

        self.ui.action_Dark_Mode.changed.connect(self.theme_toggle)

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
        self.ignore_check()

    def update_activity(self):
        activity_l = self.ui.activityList
        try:
            act_path = Path(
                activity_l.les_dirs[activity_l.cur_les]) / activity_l.cur_day / 'Activities'
            activity_list = [x for x in act_path.iterdir() if x.is_dir()]
            for activity in activity_list:
                activity_l.addItem(activity.stem)
            activity_l.update()
        except FileNotFoundError:
            self.error_box

    def ignore_check(self):
        actDone = self.ui.activitiesDone
        cur_les = self.ui.activityList.cur_les
        cur_day = self.ui.activityList.cur_day
        model = QStandardItemModel()
        try:
            ignore_path = Path(actDone.basePath[cur_les]) / '.gitignore'

            with open(ignore_path.as_posix(), 'r') as gitignore:
                line_count = 0
                act_count = 0
                for line in gitignore.read().splitlines():
                    if line.startswith(cur_day) and line.endswith('Solved'):
                        line_count += 1
                    if line.startswith('#' + cur_day):
                        if line.endswith('Solved'):
                            act = line.split('/')[2]
                            model.appendRow(QStandardItem(act))
                            act_count += 1
            try:
                progress = act_count/line_count * 100
            except ZeroDivisionError:
                progress = 100
            self.ui.lessonProgress.setValue(progress)
            QtWidgets.qApp.processEvents()
            self.ui.lessonProgress.update()
            actDone.setModel(model)
        except IndexError:
            self.error_box()

    def pushActivity(self):
        self.radioClicked()

    def error_box(self):
        error = QtWidgets.QMessageBox()
        error.setText('File path does not exist')
        error.setWindowTitle('Error')
        error.setIcon(QtWidgets.QMessageBox.Critical)
        error.exec_()

    def theme_toggle(self):
        self.settings
        if self.settings['theme'] == 'light':
            self.ui.action_Dark_Mode.setChecked(True)
            self.set_dark_mode()
        elif self.settings['theme'] == 'dark':
            self.ui.action_Dark_Mode.setChecked(False)
            self.set_light_mode()

    def set_dark_mode(self):
        print('called dark_mode')
        self.settings["theme"] = "dark"
        self.set_path.write_text(json.dumps(self.settings))
        self.dark_mode()

    def set_light_mode(self):
        print('called light_mode')
        self.settings["theme"] = "light"
        self.set_path.write_text(json.dumps(self.settings))
        self.light_mode()

    def dark_mode(self):
        darkMode = QPalette()
        darkMode.setColor(QPalette.Window, QColor(53, 53, 53))
        darkMode.setColor(QPalette.WindowText, Qt.white)
        darkMode.setColor(QPalette.Base, QColor(25, 25, 25))
        darkMode.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        darkMode.setColor(QPalette.ToolTipBase, Qt.white)
        darkMode.setColor(QPalette.ToolTipText, Qt.white)
        darkMode.setColor(QPalette.Text, Qt.white)
        darkMode.setColor(QPalette.Button, QColor(53, 53, 53))
        darkMode.setColor(QPalette.ButtonText, Qt.white)
        darkMode.setColor(QPalette.BrightText, Qt.red)
        darkMode.setColor(QPalette.Link, QColor(42, 130, 218))
        darkMode.setColor(QPalette.Highlight, QColor(42, 130, 218))
        darkMode.setColor(QPalette.HighlightedText, Qt.black)
        QtWidgets.qApp.processEvents()
        QtWidgets.qApp.setPalette(darkMode)

    def light_mode(self):
        lightMode = QPalette()
        lightMode.setColor(QPalette.Window, QColor(245, 245, 245))
        lightMode.setColor(QPalette.WindowText, Qt.black)
        lightMode.setColor(QPalette.Base, QColor(245, 245, 245))
        lightMode.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        lightMode.setColor(QPalette.ToolTipBase, Qt.black)
        lightMode.setColor(QPalette.ToolTipText, Qt.black)
        lightMode.setColor(QPalette.Text, Qt.black)
        lightMode.setColor(QPalette.Button, QColor(245, 245, 245))
        lightMode.setColor(QPalette.ButtonText, Qt.black)
        lightMode.setColor(QPalette.BrightText, Qt.red)
        lightMode.setColor(QPalette.Link, QColor(42, 130, 218))
        lightMode.setColor(QPalette.Highlight, QColor(42, 130, 218))
        lightMode.setColor(QPalette.HighlightedText, Qt.white)
        QtWidgets.qApp.processEvents()
        QtWidgets.qApp.setPalette(lightMode)


# Force the style to be the same on all OSs:
app.setStyle("Fusion")

win = Window()
win.show()

sys.exit(app.exec())
