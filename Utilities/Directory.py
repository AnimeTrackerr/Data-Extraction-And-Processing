import re
import os


class Directory:
    def __init__(self, work_dir):
        self.work_dir = work_dir

    def createDirs(self, *args):
        for file_name in args:
            path = f'{self.work_dir}/{file_name}'

            if not os.path.exists(path):
                os.makedirs(path)

    def getIncrementedFileName(self, dir_name, file_pattern, match_group):
        highest = -1

        for file in os.listdir(f'{os.getcwd()}\\{dir_name}'):
            m = re.match(file_pattern, file)

            if m:
                highest = max(highest, int(m.groups()[match_group-1]))

        return highest + 1
