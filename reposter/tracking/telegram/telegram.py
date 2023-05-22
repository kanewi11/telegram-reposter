import random
import asyncio
import traceback
from os import PathLike
from pathlib import Path
from typing import Union

import fleep
import uvloop
from pyrogram.errors import ReactionInvalid
from pyrogram.handlers import MessageHandler
from pyrogram import Client, filters, types, idle
from pyrogram.errors.exceptions.unauthorized_401 import UserDeactivatedBan, AuthKeyUnregistered

from reposter.logger import logger
from reposter.database import async_add_post


class TelegramTracker:
    app: Client = None

    EMOJIS = ['👍', '❤️', '🔥', '🥰', '👏', '😁', '🤔', '🎉', '🤩', '⚡️', '💯', '❤️‍🔥']

    this_media_id = None

    BASE_DIR = Path(__file__).parent
    WORK_DIR = BASE_DIR.joinpath('sessions')
    WORK_DIR.mkdir(exist_ok=True)
    FILES_DIR = BASE_DIR.joinpath('files')

    def __init__(self, api_id: str, api_hash: str, channel: str, phone: str, files_dir: PathLike = None) -> None:
        """ Инициализация TelegramTracker

        :param api_id: App api_id из "App configuration" -> https://my.telegram.org/apps
        :param api_hash: App api_hash из "App configuration" -> https://my.telegram.org/apps
        :param channel: Канал из которого будут браться посты, например: ссылка "https://t.me/contest" -
            вам нужно передать "contest"
        :param phone: Ваш номер телефона
        :param files_dir: Путь где будут хранится скаченные посты
        """
        uvloop.install()

        self.api_id = api_id
        self.api_hash = api_hash
        self.channel = channel
        self.phone = phone
        self.files_dir = files_dir

        if self.files_dir is None:
            self.files_dir = self.FILES_DIR

        if not isinstance(self.files_dir, Path):
            self.files_dir = Path(self.files_dir)

        self.files_dir.mkdir(exist_ok=True)

    def start(self) -> None:
        asyncio.run(self._main())

    async def _delete_session(self, name: str):
        session = self.WORK_DIR.joinpath(Path(name).with_suffix('.session'))
        if session.exists():
            session.unlink()
        await self._main()

    async def _main(self) -> None:
        self.app = Client(self.phone, workdir=self.WORK_DIR.__str__(), api_id=self.api_id,
                          api_hash=self.api_hash, phone_number=self.phone)

        handler = MessageHandler(self._handler, filters=filters.chat([self.channel]))
        self.app.add_handler(handler)

        try:
            await self.app.start()
        except AuthKeyUnregistered:
            return await self._delete_session(self.phone)

        logger.info(f'Start {self.app.name}!')

        await idle()

        await self.app.stop()

    async def _send_reaction(self, client: Client, message: types.Message) -> None:
        """Handler for sending reactions"""
        emoji = random.choice(self.EMOJIS)
        try:
            await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji=emoji)
        except ReactionInvalid:
            logger.warning(f'{emoji} - invalid reaction')
        except UserDeactivatedBan:
            logger.warning(f'Session banned - {self.app.name}')
        except Exception:
            logger.warning(traceback.format_exc())

    async def _download_post(self, _, message: types.Message) -> None:
        """Handler for download post"""
        id_ = str(message.media_group_id or message.id)

        if message.photo or message.video or message.document:

            try:
                file_dir = (await self.__create_or_get_post_dir(id_)).__str__()
                str_file_dir = file_dir if file_dir.endswith('/') else file_dir + '/'
                await self.app.download_media(message, str_file_dir)
            except UserDeactivatedBan:
                logger.warning(f'Session banned - {self.app.name}')
            except Exception:
                logger.critical(traceback.format_exc())

        text = message.caption or message.text

        if text:
            post_dir = await self.__create_or_get_post_dir(id_)
            await self._write_file(post_dir.joinpath('text.txt'), text)
            await self._write_file(post_dir.joinpath('MD_text.txt'), text.markdown)
            await self._write_file(post_dir.joinpath('HTML_text.txt'), text.html)

    async def _handler(self, client: Client, message: types.Message) -> None:
        if self.this_media_id == message.media_group_id and message.media_group_id is not None:
            return

        self.this_media_id = message.media_group_id
        await self._send_reaction(client, message)

        if message.media_group_id:
            try:
                media_group = await message.get_media_group()
                for media in media_group:
                    await self._download_post(client, media)
            except ValueError:
                logger.warning(traceback.format_exc())
            except Exception:
                logger.critical(traceback.format_exc())
        else:
            await self._download_post(client, message)

        id_ = str(message.media_group_id or message.id)
        await async_add_post((await self.__create_or_get_post_dir(id_)).__str__(), 'telegram')

    @staticmethod
    async def _write_file(file_path: Union[PathLike, str], data: Union[bytes, str]) -> None:
        if isinstance(data, bytes):
            with open(file_path, 'wb') as f:
                f.write(data)
        else:
            with open(file_path, 'w') as f:
                f.write(data)

    async def __create_or_get_post_dir(self, dir_name: str) -> Path:
        dir_path = self.files_dir.joinpath('TG' + dir_name)
        dir_path.mkdir(exist_ok=True)
        return dir_path
