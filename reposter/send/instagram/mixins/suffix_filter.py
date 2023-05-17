from typing import List
from pathlib import Path


class SuffixFilterMixin:
    suffixes = (
        '.AVI',
        '.MP4',
        '.3GP',
        '.MPEG',
        '.MOV',
        '.FLV',
        '.M4V',
        '.WMV',
        '.PNG',
        '.JPEG',
        '.JPG',
        '.HEIC',
        '.GIF',
        '.BMP',
    )

    def _filter_files(self, file_paths: List[Path]):
        for file_path in file_paths:
            if file_path.suffix.upper() not in self.suffixes:
                file_paths.remove(file_path)
        return file_paths
