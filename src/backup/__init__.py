"""
author: thomaszdxsn
"""
import logging
from abc import ABC, abstractmethod


class BackupAbstract(ABC):

    def  __init__(self):
        self.logger = logging.getLogger(f'backup.{self.__class__.__name__}')

    @abstractmethod
    def upload(self, *args):
        pass