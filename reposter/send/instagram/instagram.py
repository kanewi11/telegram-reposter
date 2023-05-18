import hashlib
import getpass
import traceback
from pathlib import Path
from typing import Union

from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired

from reposter.database import Post
from reposter.logger import logger
from reposter.send.send import Send
from reposter.post import PostMaker
from .mixins import SuffixFilterMixin


class InstPoster(SuffixFilterMixin, PostMaker, Send):
    BASE_DIR = Path(__file__).parent
    SETTINGS_DIR = BASE_DIR.joinpath('settings')
    SETTINGS_DIR.mkdir(exist_ok=True)
    SETTINGS_SUFFIX = '.json'

    bot: Client

    def __init__(self, login: str, password: str, proxy: str = None, enabled: bool = False):
        """ Инициализация InstPoster

        :param login: Логин от Instagram
        :param password: Пароль от Instagram
        :param proxy: Прокси (убедитесь что он подходит для Instagram)
        :param enabled: Включать ли постинг True или False.
        """
        self._login = login
        self.__password = password
        self.proxy = proxy
        self.enabled = enabled

        if not self._login or not self.__password:
            input('Пожалуйста вставьте логин и пароль от Instagram reposter/base.py\n'
                  'и перезапустите приложение!')
            self.enabled = False

        if not self.enabled:
            logger.info('Instagram постер выключен ❌')
            return
        logger.info('Instagram постер включен ✅')
        self.bot = Client(proxy=proxy)
        settings = self.__get_settings()
        if settings:
            self.bot.load_settings(settings)
        else:
            self._auth()

    def __get_hash(self):
        return hashlib.pbkdf2_hmac(
            'sha256',
            f'{self._login}{self.__password}'.encode('utf-8'),
            getpass.getuser(),
            100000
        )

    def __get_settings(self) -> Union[Path, None]:
        key = self.__get_hash()
        settings_file_path = self.SETTINGS_DIR.joinpath(key.decode()).with_suffix(self.SETTINGS_SUFFIX)
        return settings_file_path if settings_file_path.exists() else None

    def __save_settings(self):
        key = self.__get_hash()
        settings_file_path = self.SETTINGS_DIR.joinpath(key.decode()).with_suffix(self.SETTINGS_SUFFIX)
        self.bot.dump_settings(settings_file_path)

    def _auth(self, two_factor_code: str = None):
        if not two_factor_code:
            try:
                login = self.bot.login(username=self._login, password=self.__password)
            except TwoFactorRequired:
                print('Для входа в Instagram требуется код двухфакторной аутентификации с Google Authenticator!')
                return self._auth(input('Введите код: '))
        else:
            login = self.bot.login(username=self._login, password=self.__password,
                                   relogin=True, verification_code=two_factor_code)

        if not login:
            logger.error('NOT LOGIN INSTAGRAM')
            print('Ошибка входа Instagram!')
            self.enabled = False
            return

        self.__save_settings()

    def send_posts(self, post: Post):
        if not self.enabled:
            return

        try:
            file_paths = self._get_post_file_paths(post.dir_path)
            text, file_paths = self._make_post_data_inst(file_paths)
            file_paths = self._filter_files(file_paths)
            self.bot.album_upload(file_paths, text)
        except Exception:
            logger.error(traceback.format_exc())



