from pathlib import Path
from shutil import copytree, ignore_patterns
import json


class Settings:
    def __init__(self, lesson):
        self.settings = json.load(Path('settings.json').open())
        self.lesson_path = Path(self.settings['lessonPath'])
        self.lesson = lesson
        self.class_path = Path(self.settings['classPath'])
        self.class_day = self.settings['classDay']

        # Save yourself
        self.ignore = ignore_patterns('TimeTracker*', 'LessonPlan.md',
                                      'VideoGuide.md', '*eslintrc.json')

    def saveyourself(self):
        try:
            top_readme = self.class_path / self.lesson / 'README.md'
            top_readme.expanduser().unlink()
        except FileNotFoundError:
            pass

    def copy(self):
        if self.lesson:
            full_lesson = self.lesson_path / '01-Lesson-Plans' / self.lesson
            full_class = self.class_path / self.class_day / self.lesson
            try:
                copytree(full_lesson.expanduser().as_posix(),
                         full_class.expanduser().as_posix(), ignore=self.ignore)
                self.saveyourself()
            except FileExistsError:
                print(
                    f"{self.lesson} already exists in {str(self.class_path.expanduser())}")
                pass
        else:
            raise FileNotFoundError('Lesson Not Set')

    def homework(self):
        if self.lesson:
            lp_homework = self.lesson_path / '02-Homework' / self.lesson / 'Instructions'
            cl_homework = self.class_path / 'Homework' / self.lesson
            hw_ignore = ignore_patterns('Solutions', '*eslintrc.json')

            try:
                copytree(lp_homework.expanduser().as_posix(),
                         cl_homework.expanduser().as_posix(), ignore=hw_ignore)
            except FileExistsError:
                print(f"{self.lesson} Homework already exists")
