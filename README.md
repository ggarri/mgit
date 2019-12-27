# MultiGit
Tool to handle several packages within a workspace

## Pre-requirements
- Python 2.7 or newer
- Git 1.7 or newer
- Pip 1.5 or newer

## Setup
### Installing dependencies
```bash
$> pip install -r ./requirements.txt
```

### Config environment

Create a copy from the templated config
```bash
$> cp config/environment.yml.dist config/environment.yml
```

and edit it with your preferences
```
$ vim config/environment.yml
version: 0.1
prod_branch: origin/master
remote.default: origin
n_cpu: False
```
where:
- n_cpu: Number of cpu assigned to the mgit
- prod_branch: What it is consider your production branch
- remote.default: Git remote

### Install globally

```bash
$> ln -snf $(pwd)/main.py /usr/local/bin/mgit
```

## How to use it

`mgit` is meant to be use to handle multirepo project, so to use it you have to place yourself within one folder in which contains several repositories such us:
```bash
➜  mymultiproject tree
.
├── repository-1
├── repository-2
└── repository-3
```

then you can use regular git command across:
- every repository (`--all)
- repository only with local changes (`--only-local)
- repository in no prod branch (`--no-prod)

## Sample commands

Running pull over all repos you can run:
```bash
$> mgit pull --all
```

Create a new branch for every project with changes using:
```bash
$> mgit checkout -b new_branch --only-local
```

Commit changes on not repos using not prod branch
```bash
$> mgit commit -a -m "My commit message" --no-prod
```

## Help instructions
```
$ mgit -h
usage: mgit [-h] [--ws [WS]] [--version] [--only-local] [--all] [--no-prod]
            [--packages PACKAGES [PACKAGES ...]]
            {log,diff,status,pull,push,commit,checkout,clean,bash,reset,merge}
```
