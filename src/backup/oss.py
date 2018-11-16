"""
author: thomaszdxsn
"""
from . import BackupAbstract


class OssBackup(BackupAbstract):

    def __init__(self):
        super(OssBackup, self).__init__()

    def _upload(self, *args):
        # sync way
        pass

    async def upload(self, *args):
        pass