import sys
import time
import traceback
from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import parse_qs
from typing import List, Tuple, Union

import vk_api
from bs4 import BeautifulSoup as bs

from reposter.logger import logger
from reposter.send.vk.mixins import UploadMixin
from reposter.base.models import get_new_posts, posted


class VkPoster(UploadMixin):
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

    def __init__(self, token: str, group_id: int):
        self.__token = token
        self.group_id = group_id

        if not self.__token:
            self.make_token()

        if not self.group_id:
            input('Пожалуйста вставьте ID группы reposter/config.py в переменную VK_GROUP_ID\n'
                  'и перезапустите приложение!')
            sys.exit()

        self.__vk_auth()

    def __vk_auth(self):
        self._vk_session = vk_api.VkApi(token=self.__token)

    @staticmethod
    def _get_post_file_paths(post_dir: Path) -> List[str]:
        return [path.__str__() for path in Path(post_dir).iterdir() if path.is_file()]

    @staticmethod
    def _html_to_text(html) -> str:
        hrefs = []
        html = html.replace('\n', '||')
        soup = bs(html, 'lxml')

        for x in soup.find_all():
            if len(x.get_text(strip=True)) == 0:
                x.extract()

        a_tags = soup.find_all('a', href=True)
        for a_tag in a_tags:
            href = a_tag.get('href')
            if href in hrefs:
                continue
            hrefs.append(href)
            a_tag.append(f' ({href})')

        text = soup.get_text()
        return text.replace('||', '\n')

    def _make_post(self, file_paths: Union[List[str]]) -> Tuple[str, List[str]]:
        text = ''
        files = []
        for file_path in file_paths:
            if 'HTML_text.txt' in file_path:
                with open(file_path) as text_file:
                    text = self._html_to_text(text_file.read())
                continue
            elif 'text.txt' in file_path:
                continue
            files.append(file_path)
        return text, files

    def _send_posts(self):
        posts = get_new_posts()
        for post in posts:
            try:
                file_paths = self._get_post_file_paths(post.dir_path)
                text, file_paths = self._make_post(file_paths)
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
                logger.error(traceback.format_exc())
            posted(post.dir_path)

    def post_handler(self):
        while True:
            try:
                self._send_posts()
            except Exception:
                logger.error(traceback.format_exc())
                sys.exit()
            time.sleep(10)

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
