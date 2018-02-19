import traceback
from os import path, listdir

from git import GitCommandError

from helpers import Color
from .package import Package
from libs.args_parser import *
import inspect

class Workspace(object):
    """
    :type package: list<Package>
    """
    ws_src = None
    packages = dict()

    def __init__(self, ws_src, only_local_changes = False, only_no_prod = False, packages = None):
        self.ws_src = ws_src
        self.packages = Workspace.get_packages(ws_src)

    def run(self, git_cmd, git_args):
        """
        :param str git_cmd:
        :rtype list(str)
        """
        if len(git_cmd) == 0: return

        for package in self.packages:
            try:
                output = self.run_cmd(package, git_cmd, git_args)
            except GitCommandError as e:
                output = Color.red(e.stderr or e.stdout)
            except ValueError as e:
                output = Color.red(e.message)
            except:
                output = Color.red(traceback.format_exc())
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
        if git_cmd == 'status': return self.run_cmd_status(package, flags)
        if git_cmd == 'diff': return self.run_cmd_diff(package, flags)
        if git_cmd == 'push': return self.run_cmd_push(package, flags)
        if git_cmd == 'commit': return self.run_cmd_commit(package, flags)
        else: raise ValueError('Invalid argument "git %s" is not implemented or does not exists' % git_cmd)

    def run_cmd_log(self, package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, remote_branch = self._get_cmd_args(GitLogParser.create(), flags)
        return package.cmd_log(args, remote_branch[0], remote_branch[1])

    def run_cmd_status(self, package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, unknown = self._get_cmd_args(GitStatusParser.create(), flags)
        return package.cmd_status(args)

    def run_cmd_diff(self, package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, remote_branch = self._get_cmd_args(GitDiffParser.create(), flags)
        return package.cmd_diff(args, remote_branch[0], remote_branch[1])

    def run_cmd_pull(self, package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, remote_branch = self._get_cmd_args(GitPullParser.create(), flags)
        return package.cmd_pull(args, remote_branch[0], remote_branch[1])

    def run_cmd_push(self, package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, remote_branch = self._get_cmd_args(GitPushParser.create(), flags)
        return package.cmd_push(args, remote_branch[0], remote_branch[1])

    def run_cmd_commit(self, package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, message = self._get_cmd_args(GitCommitParser.create(), flags)
        message = ' '.join(message) if message else None
        if message and (message[0] == '\'' or message[0] == '\''): message = message[1:]
        if message and (message[-1] == '\'' or message[-1] == '\''): message = message[:-1]
        return package.cmd_commit(args, ' '.join(message) if message else None)

    def _get_cmd_args(self, parser, flags):
        """
        :param parser: ArgumentParser
        :param flags: str
        :rtype: dict
        """
        args, unknown = parser.parse_known_args(flags)
        filter_args = dict((k, v) for k, v in vars(args).iteritems() if v)

        if isinstance(parser, GitCommitParser) or isinstance(parser, GitStatusParser):
            return filter_args, unknown

        remote, branch = None, None
        if len(unknown) >= 2: remote, branch = unknown[0], unknown[1]
        elif len(unknown) >= 1:
            if '/' in unknown[0]: remote, branch = unknown[0].split('/')[0], unknown[0].split('/')[1]
            else: branch = unknown[0]
        return filter_args, [remote, branch]

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
        """)) % (package.name, '/'.join(package.get_cur_branch()), output)
        print("\n")

    @staticmethod
    def get_packages(src):
        folders = [path.join(src, f) for f in listdir(path.join(src)) if not path.isfile(path.join(src, f))]
        return [Package(pf) for pf in folders if path.isdir(path.join(pf, '.git'))]
