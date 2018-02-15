from git import Repo
from git.cmd import Git
from os import path, environ

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
        return self.git.log(**flags)

    def cmd_status(self, flags):
        return self.git.status(**flags)

    def cmd_diff(self, flags, remote, branch):
        remote = remote or environ['remote.default']
        branch = branch or self.get_cur_branch()
        self._assert_remote_branch(remote, branch)
        list_args = self._get_args_list(flags) + ['%s/%s' % (remote, branch)]
        return self.git.diff(list_args)

    def cmd_pull(self, flags, remote, branch):
        remote = remote or environ['remote.default']
        branch = branch or self.get_cur_branch()
        self._assert_remote_branch(remote, branch)
        self.git.fetch([remote])
        # Getting number of commits behind
        remote_commits = self.git.log(*['--oneline', 'HEAD..%s/%s' % (remote, branch)])
        # In case there is not commits behind leave
        if len(remote_commits) == 0: return 'Already up-to-date.'

        local_diff = self.git.status(porcelain=True).split('\n')
        try:
            if len(local_diff) > 0:
                stashed = self.git.stash(u=True)
            if branch == self.get_cur_branch():
                output = self.git.pull(remote, branch)
            else:
                output = self.git.rebase(remote, branch)
        finally:
            if 'stashed' in locals() and stashed: self.git.stash('pop')

        return output

    def _assert_remote_branch(self, remote, branch):
        available_remotes = self.get_available_remotes()
        if remote not in available_remotes: raise ValueError('Remote %s does not exists' % remote)
        available_branch = self.get_available_remote_branches(remote)
        if branch not in available_branch: raise ValueError('Branch %s does not exists' % branch)
        print('\033[1;31mIMPORTANT: Command running with %s/%s\033[0;0m' % (remote, branch))

    def _get_args_list(self, args):
        return ['--%s=%s' % (key, value) for key, value in args.items()]

    def __repr__(self):
        return "<Package: %s(%s)>" % (self.name, self.location)

    def __str__(self):
        return """
        Package: %s 
        Location: %s
        """ % (self.name, self.location)