import os.path as op
from dataclasses import dataclass

from utils.utils_path.filename_manager.filename_manager import FilenameManager


@dataclass
class DatasetFilenameManager(FilenameManager):
    dataset_folder: str
    dataset_name: str
    train_percent: int

    def __post_init__(self):
        assert isinstance(self.dataset_folder, str)
        assert isinstance(self.dataset_name, str)
        assert isinstance(self.train_percent, int)

    @property
    def parameters(self):
        return [self.dataset_folder]

    def get_equality_conditions(self, other) -> list[bool]:
        return [self.dataset_folder == other.dataset_folder,
                self.dataset_name == other.dataset_name,
                self.train_percent == other.train_percent]

    @property
    def filename(self):
        return op.join(self.folder, f"{self.dataset_name}-{self.train_percent}.npz")

    @classmethod
    def from_filename(cls, folder, filename):
        basename = filename.split('.')[0]
        dataset_name, train_percent = basename.split('-')
        return cls(dataset_folder=folder, dataset_name=dataset_name, train_percent=int(train_percent))





