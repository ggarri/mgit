import subprocess

from git import Repo, GitCommandError
from git.cmd import Git
from helpers import Color
from os import path


class Package(object):
    location = None
    name = None
    repo = None
    git = None  # type: Git

    def __init__(self, location):
        self.name = path.split(location)[-1]
        self.location = location
        self.repo = Repo(location)
        self.git = self.repo.git

    def get_cur_remote_branch(self, joint = False):
        if self.repo.head.is_detached: return "Branch detached"
        try:
            branch = self.repo.head.reference.name
            remote = next(iter([remote.name for remote in self.repo.remotes if self.repo.head.repo == remote.repo]))
        except TypeError:
            return "Branch detached"
        else:
            if joint: return '/'.join([remote, branch])
            return remote, branch

    def get_available_remotes(self):
        return [remote.name for remote in self.repo.remotes]

    def get_name(self):
        return self.name

    def get_available_local_branches(self):
        return [branch.name for branch in self.repo.branches]

    def get_available_remote_branches(self, remote_name):
        available_branches = []
        for remote in self.repo.remotes:
            if remote.name != remote_name: continue
            available_branches = [ref.remote_head for ref in remote.refs]
        return available_branches

    def cmd_log(self, flags, remote, branch):
        if remote and branch: self._assert_remote_branch(remote, branch)
        list_args = self._get_args_list(flags)
        if remote and branch:
            list_args += ['%s/%s' % (remote, branch)]
        output = self.git.log(list_args)
        if not output: output = Color.yellow("There is not changes")
        return output

    def cmd_status(self, flags):
        return self.git.status(**flags)

    def cmd_diff(self, flags, remote, branch):
        if remote and branch: self._assert_remote_branch(remote, branch)
        list_args = self._get_args_list(flags)
        if remote and branch:
            list_args += ['%s/%s' % (remote, branch)]
        output = self.git.diff(*list_args)
        if not output: output = Color.yellow("There is not changes")
        return output

    def cmd_pull(self, flags, remote, branch):
        cur_remote, cur_branch = self.get_cur_remote_branch()
        remote, branch = remote or cur_remote, branch or cur_branch
        try:
            if not self._is_behind_commit(remote, branch):
                output = 'Already up-to-date.'
            else:
                if self._has_local_changes(): stashed = self.git.stash(u=True) != u'No local changes to save'
                if branch == cur_branch:
                    output = self.git.pull(remote, branch)
                else:
                    if 'rebase' not in flags:
                        raise ValueError('Merge is not allowed. You need to use --rebase to pull')
                    output = self.cmd_rebase(remote, branch)
        finally:
            if 'stashed' in locals() and stashed: self.git.stash('pop')

        return output

    def cmd_push(self, flags, remote, branch):
        cur_remote, cur_branch = self.get_cur_remote_branch()
        remote, branch = remote or cur_remote, branch or cur_branch
        available_remotes = self.get_available_remotes()
        if remote not in available_remotes:
            raise ValueError('Remote "%s" does not exists' % remote)

        available_branch = self.get_available_remote_branches(remote)
        if 'force' in flags:
            args = self._get_args_list(flags) + [remote, branch]
            self.git.push(args)
            output = Color.green('Push --force completed')
        elif branch not in available_branch:
            output = Color.green(self.git.push(remote, branch) or 'Push completed (New Branch)')
        elif not self._is_ahead_commit(remote, branch):
            output = Color.yellow('Nothing to commit')
        else:
            if self._is_behind_commit(remote, branch):
                if 'rebase' not in flags:
                    raise ValueError('Merge is not allowed. You need to use --rebase to push')
                self.cmd_rebase(remote, branch)
            output = Color.green(self.git.push(remote, branch) or 'Push completed')

        return output

    def cmd_commit(self, flags, message):
        if not message: output = Color.red('Commit message cannot be empty')
        elif not self._has_local_changes(): output = Color.yellow('There is not local changes')
        else:
            flags['-m'] = message
            args = self._get_args_list(flags)
            output = Color.green(self.git.commit(args))

        return output

    def cmd_bash(self, bash_cmd):
        return subprocess.check_output(bash_cmd.split(' '))

    def cmd_checkout(self, flags, branch_name):
        available_branches = self.get_available_local_branches()
        if not branch_name:
            raise ValueError('Branch name missing')
        if '-b' in flags:
            if branch_name in available_branches:
                raise ValueError('Failing creating branch "%s". Already exists' % branch_name)
            args = self._get_args_list(flags) + [branch_name]
            output = self.git.checkout(args)
        if not '-b' in flags:
            if branch_name not in available_branches:
                raise ValueError('Branch "%s" does not exists.' % branch_name)
            output = self.git.checkout(branch_name)
        return Color.green(output)

    def cmd_clean(self, remote, branch):
        available_branches = self.get_available_local_branches()
        cur_remote, cur_branch = self.get_cur_remote_branch()
        if cur_branch == branch:
            raise ValueError('Cannot remove branch in use "%s"' % branch)

        if branch not in available_branches:
            output = Color.yellow('Branch "%s" was not found' % branch)
        else:
            self.git.branch(['-D', branch])
            output = Color.green('Branch "%s" was removed' % branch)

        if not remote: return output

        available_remotes = self.get_available_remotes()
        if remote not in available_remotes:
            raise ValueError('Remote "%s" was not found' % remote)
        available_remote_branches = self.get_available_remote_branches(remote)
        if branch in available_remote_branches:
            self.git.push([remote, ':'+branch])
            output += "\n" + Color.green('Remove branch "%s/%s" removed' % (remote, branch))
        else:
            output += "\n" + Color.yellow('Remote branch "%s/%s" not found' % (remote, branch))
        return output

    def cmd_rebase(self, remote, branch):
        cur_remote, cur_branch = self.get_cur_remote_branch()
        remote, branch = remote or cur_remote, branch or cur_branch
        try:
            if self._has_local_changes(): stashed = self.git.stash(u=True) != u'No local changes to save'
            output = self.git.rebase('%s/%s'%(remote,branch))
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

    def _has_local_changes(self):
        local_diff = self.git.status(porcelain=True).split('\n')
        diffs = [diff for diff in local_diff if diff]
        return len(diffs) > 0

    def _assert_remote_branch(self, remote, branch):
        available_remotes = self.get_available_remotes()
        if remote not in available_remotes: raise ValueError('Remote "%s" does not exists' % remote)
        available_branch = self.get_available_remote_branches(remote)
        if branch not in available_branch: raise ValueError('Branch "%s" does not exists' % branch)
        print(Color.yellow('IMPORTANT: Command running with %s/%s' % (remote, branch)))

    def _get_args_list(self, args):
        return ['%s%s' % (
            key if '-' in key else '--'+str(key),
            '' if type(value) == bool else (' ' if '-' in key else '=') + str(value)) \
                for key, value in args.items()]

    def __repr__(self):
        return "<Package: %s(%s)>" % (self.name, self.location)

    def __str__(self):
        return """
        Package: %s 
        Location: %s
        """ % (self.name, self.location)
