import argparse
from argparse import ArgumentParser
from os import environ

from enum import Enum

available_git_actions = ['log', 'diff', 'status', 'pull', 'push', 'rebase', 'reset']

class AppArgsParser(ArgumentParser):
    @staticmethod
    def create():
        parser = AppArgsParser(description='MGit arguments description.', prog='MultiGit')
        # Define source folder otherwise current folder
        parser.add_argument('--src', nargs='?', type=str, default=environ.get('ws.default'), dest='workspace',
                            help='workspace folder')
        parser.add_argument('--version', '-v', action='version', version='%(prog)s ' + str(environ.get('version')))
        parser.add_argument("git_cmd", help="Git command", choices=available_git_actions, type=str)
        return parser


class GitLogParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitLogParser(description='"git log" arguments ', prog='Git Log')
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        parser.add_argument('-n', type=int, dest='n', default=5)
        parser.add_argument('--oneline', type=bool, required=False, dest='oneline')
        parser.add_argument('--pretty',
                            type=str,
                            default='%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset',
                            dest='pretty')
        return parser

class GitStatusParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitStatusParser(description='"git status" arguments', prog='Git Status')
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        return parser

class GitDiffParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitDiffParser(description='"git pull" arguments', prog='Git Pull')
        parser.add_argument('--color', type=str, default='always')
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        return parser

class GitPullParser(ArgumentParser):
    @staticmethod
    def create():
        parser = GitPullParser(description='"git pull" arguments', prog='Git Pull')
        # parser.add_argument('git_cmd', nargs='*', help='Git command to execute on every package')
        return parser