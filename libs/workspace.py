
from os import path, listdir
from .package import Package
import inspect

class Workspace(object):
    """
    :type package: list<Package>
    """
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
            output = self.run_cmd(package, cmd, flags)
            self._print_cmd_output(package, output)

    def run_cmd(self, package, git_cmd, flags):
        """
        :param package: Package
        :param git_cmd: str
        :param flags: str
        :rtype: str
        """
        if git_cmd == 'log': return self.run_cmd_log(package, flags)
        else: raise ValueError('Invalid argument "git %s" is not implemented or does not exists' % git_cmd)

    def run_cmd_log(self, package, flags):
        """
        :param package: Package
        :param flags: str
        :rtype: str
        """
        return package.cmd_log(flags)

    def _print_cmd_output(self, package, output):
        """
        :param Package package:
        :param str output:
        :return:
        """
        print(inspect.cleandoc("""
        ############################
        # %s (%s)
        ############################
        % s
        """)) % (package.name, package.get_cur_branch(), output)
        print("\n")

    @staticmethod
    def get_packages(src):
        folders = [path.join(src, f) for f in listdir(path.join(src)) if not path.isfile(path.join(src, f))]
        return [Package(pf) for pf in folders if path.isdir(path.join(pf, '.git'))]
