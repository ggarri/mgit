from git import Repo, GitCommandError, RemoteReference
from git.cmd import Git
from os import path, environ
import uuid
from args_parser import GitLogParser, GitPullParser
from libs.args_parser import GitStatusParser, GitDiffParser


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

    def get_available_remotes(self):
        return [remote.name for remote in self.repo.remotes]

    def get_available_remote_branches(self, remote_name):
        available_branches = []
        for remote in self.repo.remotes:
            if remote.name != remote_name: continue
            available_branches = [ref.remote_head for ref in remote.refs]
        return available_branches

    def cmd_log(self, flags):
        args, unknown = self._get_cmd_args(GitLogParser.create(), flags)
        return self.git.log(**args)

    def cmd_status(self, flags):
        args, unknown = self._get_cmd_args(GitStatusParser.create(), flags)
        return self.git.status(**args)

    def cmd_diff(self, flags):
        args, remote_branch = self._get_cmd_args(GitDiffParser.create(), flags)
        self.assert_remote_branch(remote_branch[0], remote_branch[1])
        list_args = self._get_args_list(args, remote_branch)
        return self.git.diff(list_args)

    def cmd_pull(self, flags, remote=None, branch=None):
        args, remote_branch = self._get_cmd_args(GitPullParser.create(), flags)
        self.assert_remote_branch(remote_branch[0], remote_branch[1])
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
        finally:
            if 'stashed' in locals() and stashed: self.git.stash('pop')

        return output

    def assert_remote_branch(self, remote, branch):
        available_remotes = self.get_available_remotes()
        if remote not in available_remotes: raise ValueError('Remote %s does not exists' % remote)
        available_branch = self.get_available_remote_branches(remote)
        if branch not in available_branch: raise ValueError('Branch %s does not exists' % branch)

    def _get_args_list(self, args, unknown):
        return ['/'.join(unknown)] + ['--%s=%s' % (key, value) for key, value in args.items()]

    def _get_cmd_args(self, parser, flags):
        """
        :param parser: ArgumentParser
        :param flags: str
        :rtype: dict
        """
        args, unknown = parser.parse_known_args(flags)
        filter_args = dict((k, v) for k, v in vars(args).iteritems() if v)

        if isinstance(parser, GitPullParser) or isinstance(parser, GitDiffParser):
            remote = environ['remote.default']
            branch = self.get_cur_branch()
            if len(unknown) >= 2: remote, branch = unknown[0], unknown[1]
            elif len(unknown) >= 1:
                if '/' in unknown[0]: remote, branch = unknown[0].split('/')[0], unknown[0].split('/')[1]
                else: branch = unknown[0]
            return filter_args, [remote, branch]

        return filter_args, unknown

    def __repr__(self):
        return "<Package: %s(%s)>" % (self.name, self.location)

    def __str__(self):
        return """
        Package: %s 
        Location: %s
        """ % (self.name, self.location)