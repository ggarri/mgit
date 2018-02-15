from git import Repo, GitCommandError
from git.cmd import Git
from helpers import Color
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

    # TODO: Improve exception
    def get_cur_branch(self):
        try:
            return self.repo.head.reference.name
        except TypeError:
            return "Branch had been detached"

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

        try:
            if not self._is_behind_commit(remote, branch):
                output = 'Already up-to-date.'
            else:
                if self.is_there_local_changes(): stashed = self.git.stash(u=True)

                if branch == self.get_cur_branch(): output = self.git.pull(remote, branch)
                else:
                    if 'rebase' not in flags:
                        raise ValueError('Merge is not allowed. You need to use --rebase to pull')
                    output = self.cmd_rebase(remote, branch)
        finally:
            if 'stashed' in locals() and stashed: self.git.stash('pop')

        return output

    def cmd_push(self, flags, remote, branch):
        remote = remote or environ['remote.default']
        branch = branch or self.get_cur_branch()
        self._assert_remote_branch(remote, branch)
        if 'force' in flags:
            args = self._get_args_list(flags) + [remote, branch]
            self.git.push(args)
            output = Color.green('Push --force completed')
        elif not self._is_ahead_commit(remote, branch):
            output = Color.yellow('Nothing to commit')
        else:
            if self._is_behind_commit(remote, branch):
                if 'rebase' not in flags: raise ValueError('Merge is not allowed. You need to use --rebase to push')
                self.cmd_rebase(remote, branch)
            self.git.push(remote, branch)
            output = Color.green('Push completed')

        return output

    def cmd_rebase(self, remote, branch):
        cur_branch = self.get_cur_branch()
        try:
            if self.is_there_local_changes(): stashed = self.git.stash(u=True)
            output = self.git.rebase(remote, branch)
        except GitCommandError as e:
            self.git.rebase(abort=True)
            self.git.checkout(cur_branch)
            print(Color.red("ERR: Rebasing"))
            raise e
        finally:
            if 'stashed' in locals() and stashed: self.git.stash('pop')
        return output

    def _is_behind_commit(self, remote, branch):
        # Getting number of commits behind
        self.git.fetch([remote])
        remote_commits = self.git.log(*['--oneline', 'HEAD..%s/%s' % (remote, branch)])
        return len(remote_commits) > 0

    def _is_ahead_commit(self, remote, branch):
        # Getting number of commits behind
        self.git.fetch([remote])
        remote_commits = self.git.log(*['--oneline', '%s/%s..HEAD' % (remote, branch)])
        return len(remote_commits) > 0

    def is_there_local_changes(self):
        local_diff = self.git.status(porcelain=True).split('\n')
        return len(local_diff) > 0

    def _assert_remote_branch(self, remote, branch):
        available_remotes = self.get_available_remotes()
        if remote not in available_remotes: raise ValueError('Remote "%s" does not exists' % remote)
        available_branch = self.get_available_remote_branches(remote)
        if branch not in available_branch: raise ValueError('Branch "%s" does not exists' % branch)
        print(Color.yellow('IMPORTANT: Command running with %s/%s' % (remote, branch)))

    def _get_args_list(self, args):
        return ['--%s%s'%(key, '' if type(value) == bool else '='+value) for key, value in args.items()]

    def __repr__(self):
        return "<Package: %s(%s)>" % (self.name, self.location)

    def __str__(self):
        return """
        Package: %s 
        Location: %s
        """ % (self.name, self.location)