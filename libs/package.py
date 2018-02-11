from git import Repo, GitCommandError
from git.cmd import Git
from os import path, environ
import uuid
from args_parser import GitLogParser, GitPullParser

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

    def get_cur_branch(self):
        return self.repo.head.reference.name

    def cmd_log(self, flags):
        args, unknown = self._get_cmd_args(GitLogParser.create(), flags)
        return self.git.log(**args)

    def cmd_pull(self, flags, remote=None, branch=None):
        args, remote_branch = self._get_cmd_args(GitPullParser.create(), flags)
        if len(remote_branch) == 2: remote, branch = remote_branch[0], remote_branch[1]
        elif len(remote_branch) == 1: branch = remote_branch[0]
        if remote is None: remote = environ['remote.default']
        if branch is None: branch = self.get_cur_branch()

        try:
            # Sync first
            self.git.fetch([remote])
            remote_commits = self.git.log(*['--oneline', 'HEAD..%s/%s' % (remote, branch)])
            if len(remote_commits) == 0: return 'Already up-to-date.'
            local_diff = self.git.status(porcelain=True).split('\n')
            if len(local_diff) > 0:
                stashed = self.git.stash(u=True)
            if branch == self.get_cur_branch():
                output = self.git.pull(*remote_branch)
            else:
                output = self.git.rebase(*remote_branch)
        except GitCommandError as e:
            output = e.stderr
        finally:
            if 'stashed' in locals() and stashed: self.git.stash('pop')
        return output

    def _get_cmd_args(self, parser, flags):
        """
        :param parser: ArgumentParser
        :param flags: str
        :rtype: dict
        """
        args, unknown = parser.parse_known_args(flags)
        return dict((k, v) for k, v in vars(args).iteritems() if v), unknown

    def __repr__(self):
        return "<Package: %s(%s)>" % (self.name, self.location)

    def __str__(self):
        return """
        Package: %s 
        Location: %s
        """ % (self.name, self.location)