import os.path as op
from dataclasses import dataclass

from utils.utils_path.filename_manager.dataset_filename_manager import DatasetFilenameManager


@dataclass
class GridSearchFilenameManager(DatasetFilenameManager):
    model_name: str
    n_splits: str
    param_grid_str: str

    @property
    def folder(self) -> str:
        return '-'.join([self.dataset_folder, self.dataset_name, str(self.train_percent), self.model_name])

    def get_equality_conditions(self, other) -> list[bool]:
        res = (super().get_equality_conditions(other) + [self.model_name == other.model_name,
                                                         self.n_splits == other.n_splits,
                                                         self.param_grid_str == other.param_grid_str])
        return res

    @property
    def filename(self):
        return op.join(self.folder, f"{self.n_splits}-{self.param_grid_str}.csv")

    @classmethod
    def from_filename(cls, folder, filename):
        dataset_folder, dataset_name, train_percent, model_name = folder.split('-')
        n_splits, param_grid_str = filename.split('.csv')[0].split('-')
        return cls(dataset_folder, dataset_name, int(train_percent), model_name, n_splits, param_grid_str)
