
from os import path, listdir
from .package import Package
import inspect

class Workspace(object):
    ws_src = None
    packages = dict()

    def __init__(self, ws_src):
        self.ws_src = ws_src
        self.packages = Workspace.get_packages(ws_src)

    def run(self, git_cmd):
        """
        :param str git_cmd:
        :rtype list(str)
        """
        if len(git_cmd) == 0: return
        for package in self.packages:
            cmd = git_cmd[0]
            flags = git_cmd[1:]
            output = package.run(cmd, flags)
            self._print_cmd_output(package, output)

    def _print_cmd_output(self, package, output):
        """
        :param Package package:
        :param str output:
        :return:
        """
        print(inspect.cleandoc("""
        ############################
        #\t %s
        ############################
        % s
        """)) % (package.name, output)
        print("\n")

    @staticmethod
    def get_packages(src):
        folders = [path.join(src, f) for f in listdir(path.join(src)) if not path.isfile(path.join(src, f))]
        return [Package(pf) for pf in folders if path.isdir(path.join(pf, '.git'))]
