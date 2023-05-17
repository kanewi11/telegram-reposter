from abc import ABC, abstractmethod

from reposter.base import Post
from reposter.logger import logger


class Send(ABC):
    __enabled: bool = False

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, state: bool):
        if isinstance(state, bool):
            self.__enabled = state
        else:
            logger.warning(f'Включить и выключить можно только булевым типом данных\n'
                           f'Вы передали - {type(state)}\n'
                           f'Программа продолжит работу, но изменения в силу не вступят!')

    @abstractmethod
    def send_post(self, post: Post):
        pass
