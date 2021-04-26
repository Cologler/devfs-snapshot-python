# -*- coding: utf-8 -*-
#
# Copyright (c) 2021~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import *
import os
import sys
import ftplib
import pathlib
import re
import shutil

import ftputil
import fsoopify

def _get_dirtrees_from_fs(host, port, remotes):
    assert not port
    rv = {}
    def walk(p):
        d = {}
        for n in os.listdir(p):
            sp = os.path.join(p, n)
            if os.path.isdir(sp):
                d[n] = walk(sp)
            else:
                d[n] = None
        return d
    for remote in remotes:
        rv[remote] = walk(os.path.join(host, remote))
    return rv

class FtpSession(ftplib.FTP):
    def __init__(self, host, port, user=None, password=None):
        super().__init__()
        if port is None:
            self.connect(host)
        else:
            self.connect(host, port)
        if user and password:
            self.login(user, password)

def _get_dirtrees_from_ftp(host, port, remotes):
    rv = {}
    with ftputil.FTPHost(host=host, port=port, session_factory=FtpSession) as host:
        for remote in remotes:
            names = host.listdir(remote) # ensure is dir
            rv[remote] = dict.fromkeys(names)
    return rv

def _update_dirtree(base_dir: pathlib.Path, newtree: dict, file_suffix: str):
    base_dir.mkdir(parents=True, exist_ok=True)
    used = set()

    for name, value in newtree.items():
        if isinstance(value, dict):
            # subdir
            used.add(name)
            new_dir: pathlib.Path = base_dir / name
            if not new_dir.is_dir():
                if new_dir.exists():
                    new_dir.unlink()
            _update_dirtree(new_dir, value, file_suffix=file_suffix)

        else:
            # file
            name += '.placeholder'
            used.add(name)
            placeholder_file: pathlib.Path = base_dir / name
            if not placeholder_file.is_file():
                if placeholder_file.exists():
                    if placeholder_file.is_dir():
                        shutil.rmtree(placeholder_file)
                    else:
                        placeholder_file.unlink()
                placeholder_file.touch()

    for child in base_dir.iterdir():
        if child.name not in used:
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

def run(conf_path: str):
    conf_file = fsoopify.FileInfo(conf_path)
    if not conf_file.is_file():
        return print('%s is not a file', conf_path)
    try:
        conf: dict = conf_file.load()
    except fsoopify.SerializeError:
        return print('unable load conf file: %s', conf_path)

    # `device`
    device = conf.get('device')
    if not isinstance(device, str):
        return print('`device` is not a str')
    match = re.search(r'^(?P<host>.+):(?P<port>\d+)$', device, re.I)
    if match:
        host, port = match.group('host'), int(match.group('port'))
    else:
        host, port = device, None

    # `remotes`
    remotes: List[str] = conf.get('remotes', [])
    if isinstance(remotes, str):
        remotes = [remotes]
    elif not isinstance(remotes, list) or any(not isinstance(x, str) for x in remotes):
        return print('`remotes` is not a str list')

    # `root`
    root = conf.get('root', os.path.dirname(conf_path))
    if not isinstance(root, str):
        return print('`root` is not a str')

    # `filesuffix`
    file_suffix: str = conf.get('file_suffix', '.placeholder')
    if not isinstance(file_suffix, str):
        return print('`file_suffix` is not a str')

    if host.startswith('ftp://'):
        dirtrees = _get_dirtrees_from_ftp(host[6:], port, remotes)
    else:
        dirtrees = _get_dirtrees_from_fs(host, port, remotes)

    root_path = pathlib.Path(root)
    for remote in remotes:
        dirtree = dirtrees[remote]
        assert isinstance(dirtree, dict)
        base_dir: pathlib.Path = root_path / remote.replace(':', '')
        base_dir.mkdir(parents=True, exist_ok=True)
        _update_dirtree(base_dir, dirtree, file_suffix=file_suffix)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    args = argv[1:]
    if not args:
        return print('missing args (config file path)')

    for conf_path in args:
        run(conf_path)

if __name__ == '__main__':
    main()
