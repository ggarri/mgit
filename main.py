#!/usr/bin/env python2.7

import yaml
from os import path, environ, getcwd

from libs.args_parser import AppArgsParser
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
    parser = AppArgsParser.create()
    args, git = parser.parse_known_args()
    ws = Workspace(path.join(CUR_DIR, args.workspace or getcwd()))
    if not args.git_cmd: parser.print_help()
    ws.run(args.git_cmd, git)