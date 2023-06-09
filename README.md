# Автоматический репост из Telegram во Вконтакте и Instagram

Отслеживание и скачивание постов в Telegram происходит юзерботом ([Pyrogram](https://github.com/pyrogram/pyrogram)).

**Постинг:**
* **Вконтакте** при помощи библиотеки [vk_api](https://github.com/python273/vk_api?ysclid=lhynyiz1a2179475884)
* **Instagram** при помощи библиотеки [instagrapi](https://github.com/adw0rd/instagrapi?ysclid=lhynzfh470616898377)

## Инструкция

**Установка:**
1. `git clone https://github.com/kanewi11/telegram-reposter.git`
2. `cd telegram-reposter`
3. `pip3 install -r requirements.txt` для *nix или `pip install -r requirements_win.txt` для Windows

**Настройка:**
1. Для **Telegram** вам нужно [создать приложение](https://my.telegram.org/apps).
После внести `App api_id`, `App api_hash`, ваш номер телефона и канал в `reposter/config.py`
2. Для **Вконтакте** тоже нужно [создать Standalone-приложение](https://vk.com/editapp?act=create). 
После создания запустите `reposter.py`, далее в консоли будет инструкция как создать токен, следуйте ей.
После получения токена, закройте программу, перейдите в `reposter/config.py` в `VK_ACCESS_TOKEN` вставьте созданный токен.
Пример `VK_ACCESS_TOKEN = 'vk.b.aSd...'`. Еще не забудьте вставить id сообщества `VK_GROUP_ID`!
3. Для **Instagram** нужен прокси, логин и пароль. Если стоит двухфакторная аутентификация, то добавьте способ получения кода через приложение `Google Authenticator`.

Можно включать и отключать постинг в определенные соцсети. 
В файле `reposter/config.py` в переменных `REPOST_VK` и `REPOST_INST`. 
* `True` - Включен
* `False` - Выключен

**Instagram по дефолту ВЫКЛЮЧЕН**

### Предостережение

**Все пароли и токены хранятся в `config.py` и это очень плохо, лучше всего храните их в переменных окружения!**
_Если вы решили хранить их в файле, то при утечке пенайте на себя!_
