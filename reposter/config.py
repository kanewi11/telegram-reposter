from pathlib import Path


# -------------------------- Telegram --------------------------
# https://my.telegram.org
API_ID = 1234567
API_HASH = 'asdkapdokapodkapokdaposd'

PHONE = '+79876543212'
# Your tg channel. Example: https://t.me/contest
CHANNEL = 'contest'

# -------------------------- Вконтакте --------------------------
VK_ACCESS_TOKEN = 'vk1.a.IADHiudahsdajhdi...'
VK_GROUP_ID = 123456789

# -------------------------- Не разбираешься - не трогай! --------------------------
BASE_DIR = Path(__file__).parent
FILES_DIR = BASE_DIR.joinpath('files')
LOGS_DIR = BASE_DIR.joinpath('logs')

paths = [FILES_DIR, LOGS_DIR, ]

for path in paths:
    path.mkdir(exist_ok=True)
