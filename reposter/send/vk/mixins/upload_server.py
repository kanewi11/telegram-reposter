from pathlib import Path
from typing import Any, List

import vk_api
from vk_api import VkUpload


class UploadMixin:
    _vk_session: vk_api.VkApi
    group_id: int

    video = ['.AVI', '.MP4', '.3GP', '.MPEG', '.MOV', '.FLV', '.M4V', '.WMV']
    photo = ['.PNG', '.JPEG', '.JPG', '.HEIC', '.GIF', '.BMP']

    def _get_attachment(self, file_paths: List[str]) -> Any:
        uploads = []
        for file_path in file_paths:
            suffix = Path(file_path).suffix
            upload = VkUpload(self._vk_session)
            file_path = file_path.__str__()
            if suffix.upper() in self.video:
                response = upload.video(file_path, group_id=self.group_id)
                uploads.append('video{owner_id}_{video_id}'.format(**response))
            elif suffix.upper() in self.photo:
                response = upload.photo_wall(file_path, group_id=self.group_id)
                uploads.append(','.join('photo{owner_id}_{id}'.format(**item) for item in response))
            else:
                response = upload.document_wall(file_path)
                uploads.append('doc{owner_id}_{id}'.format(**response.get('doc')))
        return ','.join(uploads) or None
