import traceback
from os import path, listdir
import time
import inspect

from git import GitCommandError

from helpers import Color
from .package import Package
from libs.args_parser import *

pool_packages = set()

def execute_package(package, git_cmd, git_args):
    """
    :param Package package:
    :param str git_cmd:
    :param list git_args:
    :rtype str:
    """
    try:
        output = Workspace.run_cmd(package, git_cmd, git_args)
    except GitCommandError as e:
        output = Color.red(e.stderr or e.stdout)
    except ValueError as e:
        output = Color.red(e.message)
    except:
        output = Color.red(traceback.format_exc())
    return output

def competed_package(package, output):
    """
    :param Package package:
    :param str output:
    """
    pool_packages.remove(package.get_name())
    Workspace._print_cmd_output(package, output)



class Workspace(object):
    """
    :type packages: list<Package>
    :type pool: multiprocessing.Pool
    """
    workspace = None
    pool = None
    packages = dict()
    git_cmd = None
    git_args = []
    parser = None

    def __init__(self, cwd, pool = None):
        parser = AppArgsParser.create()
        args, self.git_args = parser.parse_known_args()
        if not args.git_cmd: parser.print_help(); return

        self.git_cmd = args.git_cmd
        self.workspace = args.ws or cwd
        self.pool = pool
        self.packages = Workspace.get_packages(
            self.workspace,
            all_packages=args.all_packages,
            only_local_changes = args.only_local,
            only_no_prod = args.no_prod,
            package_names = (args.packages or list())
        )

    def run(self):
        """
        :param str git_cmd:
        :rtype list(str)
        """
        if len(self.packages) == 0:
            print(Color.red('There is not packages selected'))
            exit(-1)

        global pool_packages
        print(Color.yellow('Following command "git %s" is about to run on:\n' % self.git_cmd))
        for package in self.packages: print("\t" + package.get_name())
        # raw_input(Color.green('\n\nPress Enter to continue...'))

        for package in self.packages:
            pool_packages.add(package.get_name())
            if self.pool:
                self.pool.apply_async(execute_package, [package, self.git_cmd, self.git_args],
                                      callback=lambda output, package=package: competed_package(package, output))
            else:
                output = execute_package(package, self.git_cmd, self.git_args)
                competed_package(package, output)

        if not self.pool: return

        try:
            while len(pool_packages):
                print "Waiting packages: %s" % str(pool_packages)
                time.sleep(1)
        except KeyboardInterrupt: terminate = True; print "Interrupt!!!"
        else: terminate = False;

        if terminate: self.pool.terminate()
        print "Waiting threads to complete"; self.pool.close()
        print "Waiting threads to wrap-up"; self.pool.join()

    @staticmethod
    def run_cmd(package, git_cmd, flags):
        """
        :param package: Package
        :param git_cmd: str
        :param flags: str
        :rtype: str
        """
        if git_cmd == 'log': return Workspace.run_cmd_log(package, flags)
        if git_cmd == 'pull': return Workspace.run_cmd_pull(package, flags)
        if git_cmd == 'status': return Workspace.run_cmd_status(package, flags)
        if git_cmd == 'diff': return Workspace.run_cmd_diff(package, flags)
        if git_cmd == 'push': return Workspace.run_cmd_push(package, flags)
        if git_cmd == 'commit': return Workspace.run_cmd_commit(package, flags)
        if git_cmd == 'checkout': return Workspace.run_cmd_checkout(package, flags)
        if git_cmd == 'clean': return Workspace.run_cmd_clean(package, flags)
        if git_cmd == 'bash': return Workspace.run_cmd_bash(package, flags)
        if git_cmd == 'reset': return Workspace.run_cmd_reset(package, flags)
        if git_cmd == 'merge': return Workspace.run_cmd_merge(package, flags)
        else: raise ValueError('Invalid argument "git %s" is not implemented or does not exists' % git_cmd)

    @staticmethod
    def run_cmd_log(package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, remote_branch = Workspace._get_cmd_args(GitLogParser.create(), flags)
        return package.cmd_log(args, remote_branch[0], remote_branch[1])

    @staticmethod
    def run_cmd_status(package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, unknown = Workspace._get_cmd_args(GitStatusParser.create(), flags)
        return package.cmd_status(args)

    @staticmethod
    def run_cmd_diff(package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, remote_branch = Workspace._get_cmd_args(GitDiffParser.create(), flags)
        return package.cmd_diff(args, remote_branch[0], remote_branch[1])

    @staticmethod
    def run_cmd_pull(package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, remote_branch = Workspace._get_cmd_args(GitPullParser.create(), flags)
        return package.cmd_pull(args, remote_branch[0], remote_branch[1])

    @staticmethod
    def run_cmd_merge(package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, remote_branch = Workspace._get_cmd_args(GitMergeParser.create(), flags)
        return package.cmd_merge(remote_branch[0], remote_branch[1])

    @staticmethod
    def run_cmd_push(package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, remote_branch = Workspace._get_cmd_args(GitPushParser.create(), flags)
        return package.cmd_push(args, remote_branch[0], remote_branch[1])

    @staticmethod
    def run_cmd_commit(package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        args, message = Workspace._get_cmd_args(GitCommitParser.create(), flags)
        message = ' '.join(message) if message else None
        if message and (message[0] == '\'' or message[0] == '\''): message = message[1:]
        if message and (message[-1] == '\'' or message[-1] == '\''): message = message[:-1]
        return package.cmd_commit(args, message)

    @staticmethod
    def run_cmd_bash(package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        bash_cmd = Workspace._get_cmd_args(GitBashParser.create(), flags)
        return package.cmd_bash(bash_cmd)

    @staticmethod
    def run_cmd_checkout(package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        parser = GitCheckoutParser.create()
        args, remote_branch = Workspace._get_cmd_args(parser, flags)
        if '-b' in args:
            remote_name, branch_name = remote_branch[0], remote_branch[1]
            _from = ('%s/%s'%(remote_name, branch_name)) if remote_name else branch_name
            return package.cmd_checkout(args, branch_name=args['-b'], from_branch=_from)
        else:
            return package.cmd_checkout(args, branch_name=remote_branch[1])

    @staticmethod
    def run_cmd_clean(package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        parser = GitCheckoutParser.create()
        args, remote_branch = Workspace._get_cmd_args(parser, flags)
        return package.cmd_clean(remote_branch[0], remote_branch[1])

    @staticmethod
    def run_cmd_reset(package, flags):
        """
        :param package: Package
        :param flags: list(str)
        :rtype: str
        """
        parser = GitResetParser.create()
        args, remote_branch = Workspace._get_cmd_args(parser, flags)
        return package.cmd_reset(args, remote_branch[0], remote_branch[1])

    @staticmethod
    def _get_cmd_args(parser, flags):
        """
        :param parser: ArgumentParser
        :param flags: str
        :rtype: dict
        """
        args, unknown = parser.parse_known_args(flags)
        filter_args = dict((k, v) for k, v in vars(args).iteritems() if v)

        if isinstance(parser, GitBashParser):
            return unknown[0]
        if isinstance(parser, GitCommitParser) or isinstance(parser, GitStatusParser):
            return filter_args, unknown

        remote, branch = None, None
        if len(unknown) >= 2: remote, branch = unknown[0], unknown[1]
        elif len(unknown) >= 1:
            if '/' in unknown[0]: remote, branch = unknown[0].split('/')[0], unknown[0].split('/')[1]
            else: branch = unknown[0]
        return filter_args, [remote, branch]

    @staticmethod
    def _print_cmd_output(package, output):
        """
        :param Package package:
        :param str output:
        :return:
        """
        cur_remote, cur_branch = package.get_cur_remote_branch()
        print(inspect.cleandoc("""
        ############################
        # %s (%s)
        ############################
        % s
        """)) % (package.name, cur_branch, output)
        print("\n")

    @staticmethod
    def get_packages(src, all_packages, only_local_changes, only_no_prod, package_names):
        """
        :param string src: Source path
        :param bool only_local_changes:
        :param book only_no_prod:
        :param list(string) packages:
        :return:
        """
        folders = [path.join(src, f) for f in listdir(path.join(src)) if not path.isfile(path.join(src, f))]
        packages = [Package(pf) for pf in folders if path.isdir(path.join(pf, '.git'))]
        if len(packages) == 0:
            print(Color.red('Empty workspace. None found `./*/.git` folders'))
            exit(-1)

        return [package for package in packages
                if all_packages
                or (only_local_changes and package._has_local_changes())
                or (packages and package.get_name() in package_names)
                or (only_no_prod and package.get_cur_remote_branch(True) != environ['prod_branch'])]
