#!/usr/bin/env python2.7

import yaml
from libs.helpers import LoggingPool
from os import path, environ, getcwd

from libs.workspace import Workspace

CUR_DIR = path.dirname(path.realpath(__file__))

with open(path.join(CUR_DIR, "config/environment.yml"), 'r') as stream:
    try:
        custom_env = yaml.load(stream)
        for key, value in custom_env.items():
            environ[key] = str(value)
    except yaml.YAMLError as exc:
        print(exc)

if __name__ == "__main__":
    pool = LoggingPool(processes=int(environ['n_cpu'])) \
        if 'n_cpu' in environ and environ['n_cpu'].isdigit() else None
    ws = Workspace(cwd=path.join(CUR_DIR, getcwd()), pool=pool)
    ws.run()