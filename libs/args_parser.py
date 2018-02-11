import argparse
from os import environ

class AppArgsParser():
    @staticmethod
    def create():
        parser = argparse.ArgumentParser(description='MGit arguments description.', prog='MultiGit')
        # Define source folder otherwise current folder
        parser.add_argument('--src', nargs='?', type=str, default=environ.get('ws.default'), dest='workspace',
                            help='workspace folder')
        parser.add_argument('--version', '-v', action='version', version='%(prog)s ' + str(environ.get('version')))
        return parser


class GitLogParser():
    @staticmethod
    def create():
        parser = argparse.ArgumentParser(description='"git log" arguments ', prog='Git Log')
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        parser.add_argument('-n', type=int, dest='n', default=5)
        parser.add_argument('--oneline', type=bool, required=False, dest='oneline')
        parser.add_argument('--pretty',
                            type=str,
                            default='%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset',
                            dest='pretty')
        return parser

class GitPullParser():
    @staticmethod
    def create():
        parser = argparse.ArgumentParser(description='"git pull" arguments', prog='Git Pull')
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        return parser