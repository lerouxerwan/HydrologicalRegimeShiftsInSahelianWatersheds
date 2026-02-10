from abc import ABC
from dataclasses import dataclass

from utils.utils_path.filename_manager.utils_filename_manager import SEPARATOR


class FilenameManager(ABC):
    """Object to help handling filenames of saved objects"""

    def __eq__(self, other):
        return all(self.get_equality_conditions(other))

    def get_equality_conditions(self, other) -> list[bool]:
        raise NotImplementedError

    @classmethod
    def from_filename(cls, folder, filename):
        raise NotImplementedError

    @property
    def parameters(self):
        raise NotImplementedError

    @property
    def folder(self) -> str:
        return SEPARATOR.join(self.parameters)

    @property
    def filename(self):
        raise NotImplementedError
