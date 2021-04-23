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

import ftputil

class FtpSession(ftplib.FTP):
    def __init__(self, host, port, user=None, password=None):
        super().__init__()
        self.connect(host, port)
        if user and password:
            self.login(user, password)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    local_root = os.path.expandvars(r'%OneDrive%\Devices\PSVita\DevfsSnapshot')
    local_root_path = pathlib.Path(local_root)

    remotes = [
        r'ux0:/pspemu/ISO'
    ]

    with ftputil.FTPHost(host='192.168.1.103', port=1337, session_factory=FtpSession) as host:
        for remote in remotes:
            names = host.listdir(remote) # ensure is dir
            local_path = local_root_path / remote.replace(':', '')
            local_path.mkdir(parents=True, exist_ok=True)
            placeholders = set(n + '.placeholder' for n in names)
            for placeholder in placeholders:
                (local_path / placeholder).touch()
            for child in local_path.iterdir():
                if child.name not in placeholders:
                    child.unlink()

if __name__ == '__main__':
    main()
