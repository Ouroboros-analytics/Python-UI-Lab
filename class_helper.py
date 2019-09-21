from PyQt5 import QtWidgets
from ui import Ui_MainWindow
from settings import Settings
import sys
import subprocess
from pathlib import Path
from os.path import expanduser
from PyQt5.QtGui import QKeySequence, QPalette, QColor, QStandardItem, QStandardItemModel, QIcon
from PyQt5.QtCore import Qt, pyqtSlot, QSize, QDir
import json
import shutil
import pprint
import ctypes
myappid = u'Class Helper'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

app = QtWidgets.QApplication(sys.argv)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.set_path = Path('settings.json')
        if self.set_path.exists():
            self.settings = json.load(self.set_path.open())
        else:
            pass

        lessons = Path(self.settings['lessonPath']
                       ).expanduser() / '01-Lesson-Plans'
        lessons_dirs = [x for x in lessons.iterdir() if x.is_dir()]
        for lesson in lessons_dirs:
            self.ui.lessonList.addItem(lesson.stem)
        self.ui.activityList.les_dirs = lessons_dirs

        if self.settings['lessonPath'] is not 'None':
            self.ui.action_Set_Lesson_Plans.setChecked(True)

        if self.settings['classPath'] is not 'None':
            self.ui.action_Set_Class_Repo.setChecked(True)

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

        if self.settings['commitMsg'] == 'Lesson_Name - Solved':
            self.ui.actionLesson_Name_Solved.setChecked(True)
        elif self.settings['commitMsg'] == '00 - Solved':
            self.ui.action00_Solved.setChecked(True)
        elif self.settings['commitMsg'] == '00 - Lesson_name - Solved':
            self.ui.action00_Lesson_name_Solved.setChecked(True)

        self.ui.commit_group.triggered.connect(self.commit_msg)

        if self.settings['pushStyle'] == 'All Unsolved':
            self.ui.actionAll_Unsolved.setChecked(True)
        elif self.settings['pushStyle'] == 'One Activity':
            self.ui.actionOne_Activity.setChecked(True)

        self.ui.setup_group.triggered.connect(self.setup_style)

        # self.ui.pushActivity.clicked.connect(self.push_activity)

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

    def commit_msg(self):
        active = self.ui.commit_group.checkedAction()
        print(active.text())

        self.settings['commitMsg'] = active.text()
        self.set_path.write_text(json.dumps(self.settings))

    def setup_style(self):
        active = self.ui.setup_group.checkedAction()
        print(active.text())

        self.settings['pushStyle'] = active.text()
        self.set_path.write_text(json.dumps(self.settings))

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

    def dir_view(self):
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(str(Path('~').expanduser()))
        self.view = QtWidgets.QTreeView()
        self.view.setModel(self.model)
        print(self.view.treePosition)


class SecondWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(SecondWindow, self).__init__()
        self.settings = Settings()
        self.model = QtWidgets.QFileSystemModel()
        home = expanduser('~')
        self.model.setRootPath(home)
        self.model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Hidden)
        self.view = QtWidgets.QTreeView()
        self.view.setModel(self.model)
        self.view.setWindowTitle('Choose Lesson Plans Directory')
        self.view.setFixedSize(500, 300)
        self.view.setRootIndex(self.model.index())
        self.view.hideColumn(1)
        self.view.hideColumn(2)
        self.view.hideColumn(3)
        self.view.show()


app.setStyle("Fusion")
app_icon = QIcon()
app_icon.addFile('img/toolbox.png', QSize(32, 32))
app.setWindowIcon(app_icon)

if Path('settings.json').exists():
    win = Window()
    win.show()
else:
    second_win = SecondWindow()


sys.exit(app.exec())
