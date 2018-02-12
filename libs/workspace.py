
from os import path, listdir, environ

from git import GitCommandError

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
            try:
                output = self.run_cmd(package, cmd, flags)
            except GitCommandError as e:
                output = e.stderr
            except ValueError as e:
                output = e.message
            self._print_cmd_output(package, output)

    def run_cmd(self, package, git_cmd, flags):
        """
        :param package: Package
        :param git_cmd: str
        :param flags: str
        :rtype: str
        """
        if git_cmd == 'log': return self.run_cmd_log(package, flags)
        if git_cmd == 'pull': return self.run_cmd_pull(package, flags)
        if git_cmd == 'sync': return self.run_cmd_sync(package, flags)
        if git_cmd == 'status': return self.run_cmd_status(package, flags)
        if git_cmd == 'diff': return self.run_cmd_diff(package, flags)
        else: raise ValueError('Invalid argument "git %s" is not implemented or does not exists' % git_cmd)

    def run_cmd_log(self, package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        return package.cmd_log(flags)

    def run_cmd_pull(self, package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        return package.cmd_pull(flags)

    def run_cmd_status(self, package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        return package.cmd_status(flags)

    def run_cmd_diff(self, package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        return package.cmd_diff(flags)

    def run_cmd_sync(self, package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        remote = environ['master_branch'].split('/')[0] if '/' in environ['master_branch'] else 'origin'
        branch = environ['master_branch'].split('/')[1] if '/' in environ['master_branch'] else environ['master_branch']
        return package.cmd_pull(flags, remote, branch)

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
