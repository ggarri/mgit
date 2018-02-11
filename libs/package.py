from git import Repo
from git.cmd import Git
from os import path

from args_parser import GitLogParser

class Package(object):
    location = None
    name = None
    repo = None
    git = None # type: Git

    def __init__(self, location):
        self.name = path.split(location)[-1]
        self.location = location
        self.repo = Repo(location)
        self.git = self.repo.git

    def run(self, cmd, flags):
        """
        :param str cmd:
        :rtype: list(str)
        """
        if cmd == 'log':
            return self.cmd_log(flags)

    def cmd_log(self, flags):
        parser = GitLogParser.create()
        args, unknown = parser.parse_known_args(flags)
        log_args = dict((k, v) for k, v in vars(args).iteritems() if v)
        return self.git.log(**log_args)

    def __repr__(self):
        return "<Package: %s(%s)>" % (self.name, self.location)

    def __str__(self):
        return """
        Package: %s 
        Location: %s
        """ % (self.name, self.location)