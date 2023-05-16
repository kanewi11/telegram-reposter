import sys
import traceback
from typing import Union
from urllib.parse import urlparse
from urllib.parse import parse_qs

import vk_api

from reposter.logger import logger
from reposter.post import PostMaker
from reposter.base.models import Post
from reposter.send.vk.mixins import UploadMixin


class VkPoster(UploadMixin, PostMaker):
    _vk_session: vk_api.VkApi = None
    group_id: int = None
    __token: str = None

    _access_key_url = 'https://oauth.vk.com/authorize' \
                      '?client_id={app_id}' \
                      '&display=page' \
                      '&redirect_uri=https://oauth.vk.com/blank.html' \
                      '&scope=friends,photos,video,stories,docs,groups,wall,offline' \
                      '&response_type=token' \
                      '&v=5.131' \
                      '&state=123456'

    def __init__(self, token: str, group_id: int, enabled: bool):
        self.__token = token
        self.group_id = group_id
        self.enabled = enabled

        if not self.enabled:
            return

        if not self.__token:
            self.make_token()

        if not self.group_id:
            input('Пожалуйста вставьте ID группы reposter/config.py в переменную VK_GROUP_ID\n'
                  'и перезапустите приложение!')
            sys.exit()

        self.__vk_auth()

    def __vk_auth(self):
        self._vk_session = vk_api.VkApi(token=self.__token)

    def send_posts(self, post: Post):
        if not self.enabled:
            return

        try:
            file_paths = self._get_post_file_paths(post.dir_path)
            text, file_paths = self.make_post_vk(file_paths)
            attachment = self._get_attachment(file_paths)

            post_data = self._vk_session.method('wall.post', {
                                'owner_id': f'-{self.group_id}',
                                'message': text,
                                'attachment': attachment,
                            })
            post_id = post_data.get('post_id')
            if post_id:
                self._vk_session.method('likes.add', {
                    'type': 'post',
                    'owner_id': f'-{self.group_id}',
                    'item_id': post_id,
                })
        except Exception:
            logger.error('VK ' + traceback.format_exc())

    def make_token(self):
        print('Для начала создайте "Standalone-приложение" и назовите его как-нибудь.\n'
              'Вот ссылка по которой это можно сделать:\n\n'
              'https://vk.com/editapp?act=create\n')
        print('-' * 50, '\n')

        app_id = input('Введите id вашего standalone-приложения: ')

        url = self.get_url_access_key(app_id)

        print(f'Перейдите по ссылке -> {url}\n'
              f'Дайте доступ, после того как высветится надпись\n\n'
              f'"Пожалуйста, не копируйте данные из адресной строки для сторонних сайтов.\n'
              f'Таким образом Вы можете потерять доступ к Вашему аккаунту."\n\n')

        access_url = input('Скопируйте ссылку и вставьте ее сюда: ')
        token = self.get_token_from_url(access_url)

        print('-' * 50)
        print(f'\n\n'
              f'Вот ваш токен, скопируйте его и вставьте его в reposter/config.py в переменную VK_ACCESS_TOKEN\n\n'
              f'{token}\n\n'
              f'и перезапустите приложение!')
        input()
        sys.exit()

    def get_url_access_key(self, app_id: Union[int, str]):
        return self._access_key_url.format(app_id=app_id)

    @staticmethod
    def get_token_from_url(url: str):
        parsed_url = urlparse(url.replace('blank.html#', 'blank.html?'))
        return parse_qs(parsed_url.query)['access_token'][0]
