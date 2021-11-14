#!/usr/bin/env python
# -*- coding:utf-8 -*-
# hello

import os
import sys
import time
import subprocess
import yaml

GIT_IGNORE_TEMPLATE = ['.deploy_git/\n'
                       'node_modules/\n'
                       'public/\n'
                       'db.json\n'
                       'package-lock.json\n'
                       ]


def find_hexo():
    curdir = os.getcwd()
    olddir = None
    while curdir != olddir:
        hexo_module = os.path.join(curdir, 'node_modules')
        hexo_config = os.path.join(curdir, '_config.yml')
        if os.path.isdir(hexo_module) and os.path.isfile(hexo_config):
            return curdir
        else:
            olddir = curdir
            curdir = os.path.dirname(curdir)
    return None


def run_commands(commands):
    for cmd in commands:
        print(f'# {cmd}')
        subprocess.run(cmd, shell=True, cwd=hexo)


if __name__ == "__main__":
    # find the root directory of hexo
    hexo = find_hexo()
    if hexo is None:
        print('not in a hexo directory')
        sys.exit(0)
    print('hexo path: ' + hexo)

    # check .git directory
    git_init = False
    if not os.path.isdir(os.path.join(hexo, '.git')):
        commands = ['git init', 'git checkout -b backup']
        run_commands(commands)
        git_init = True

    # check and create .gitignore file
    file_gitignore = os.path.join(hexo, '.gitignore')
    if not os.path.isfile(file_gitignore):
        print('file .gitignore is not exist')
        with open(file_gitignore, 'w') as f:
            f.writelines(GIT_IGNORE_TEMPLATE)
    elif git_init:
        with open(file_gitignore, 'a+') as f:
            f.write('\n')
            f.writelines(GIT_IGNORE_TEMPLATE)

    # parse _config.yml file
    with open(os.path.join(hexo, '_config.yml')) as cfg:
        hexo_yml = yaml.safe_load(cfg.read())
        backup = hexo_yml.get('backup', None)
        if backup is None:
            print('no \'backup\' configuration in _config.yml')
        else:
            repository = backup.get('repository', None)
            if repository:
                for key, val in repository.items():
                    print(f'{key}: {val}')
                    list = val.split(',')
                    if len(list) != 2:
                        print(f'invalid configuration: {key}')
                    else:
                        remote, branch = list[0].strip(), list[1].strip()
                        if git_init:
                            this_file = os.path.basename(sys.argv[0])
                            commands = [f'git remote add origin {remote}',
                                        f'git fetch origin {branch}',
                                        f'cp -f {this_file} ../_hexo_{this_file}',
                                        f'ls -al ../_hexo_{this_file}',
                                        f'git reset --hard origin/{branch}',
                                        f'mv -f ../_hexo_{this_file} {this_file}',
                                        f'git branch --set-upstream-to=origin/{branch}']
                            run_commands(commands)
                        
                        now = time.strftime(
                            "%Y-%m-%d %H:%M:%S", time.localtime())
                        commands = ['git add .',
                                    f'git commit -m "{now}"',
                                    f'git push origin HEAD:{branch} -f']
                        run_commands(commands)
