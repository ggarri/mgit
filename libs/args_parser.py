from argparse import ArgumentParser
from os import environ

available_git_actions = ['log', 'diff', 'status', 'pull', 'push', 'commit', 'checkout', 'clean', 'bash']

class AppArgsParser(ArgumentParser):
    @staticmethod
    def create():
        parser = AppArgsParser(description='MGit arguments description.', prog='mgit')
        # Define source folder otherwise current folder
        parser.add_argument('--ws', nargs='?', type=str, dest='ws', help='workspace folder')
        parser.add_argument('--version', '-v', action='version', version='%(prog)s ' + str(environ.get('version')))
        parser.add_argument('--only-local', action='store_true', dest='only_local',
                            help='Only use packages with local changes')
        parser.add_argument('--all', action='store_true', dest='all_packages',
                            help='use all packages')
        parser.add_argument('--no-prod', action='store_true', dest='no_prod',
                            help='Only use packages on prod(%s) branch' % str(environ.get('prod_branch')))
        parser.add_argument('--packages', type=str, nargs='+', required=False, dest='packages',
                            help='List of packages to use')
        parser.add_argument("git_cmd", help="Git command", choices=available_git_actions, type=str)
        return parser


class GitLogParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitLogParser(description='"git log" arguments ', prog='mgit Log')
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        parser.add_argument('-n', type=int, dest='-n', default=5)
        parser.add_argument('--oneline', type=bool, required=False, dest='oneline')
        parser.add_argument('--pretty',
                            type=str,
                            default='%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset',
                            dest='pretty')
        return parser

class GitStatusParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitStatusParser(description='"git status" arguments', prog='mgit Status')
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        return parser

class GitDiffParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitDiffParser(description='"git pull" arguments', prog='mgit Pull')
        parser.add_argument('--color', type=str, default='always')
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        return parser

class GitPullParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitPullParser(description='"git pull" arguments', prog='mgit Pull')
        parser.add_argument('--rebase', dest='rebase', action='store_true', required=False,
                            help='Include git --rebase action')
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        return parser

class GitPushParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitPushParser(description='"git pull" arguments', prog='mgit Pull')
        parser.add_argument('--rebase', dest='rebase', action='store_true', required=False,
                            help='Include git --rebase action')
        parser.add_argument('--force', dest='force', action='store_true', required=False,
                            help='Include git --force action')
        return parser

class GitCommitParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitCommitParser(description='"git commit" arguments', prog='mgit commit')
        parser.add_argument('-a', dest='-a', action='store_true', required=False, help="Adding new files")
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        return parser

class GitBashParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitBashParser(description='"bash" command', prog='mgit bash')
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        return parser

class GitCheckoutParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitCheckoutParser(description='"git checkout" arguments', prog='mgit checkout')
        parser.add_argument('-b', dest='-b', action='store_true', required=False, help="Create new branch")
        parser.add_argument('--upstream', dest='upstream', action='store_true', required=False, help="Set upstream")
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        return parser

class GitCleanParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitCleanParser(description='"git branch -D {branch}; git push {remote} :{branch}" arguments',
                                   prog='mgit clean')
        return parser