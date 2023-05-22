from pathlib import Path


# -------------------------- Telegram --------------------------

# https://my.telegram.org
API_ID = 1234567
API_HASH = 'asdkapdokapodkapokdaposd'
PHONE = '+79876543212'
# Your tg channel. Example: https://t.me/contest
CHANNEL = 'contest'

# -------------------------- Вконтакте --------------------------

REPOST_VK = True
VK_ACCESS_TOKEN = ''
VK_GROUP_ID = 123456789

# -------------------------- Instagram --------------------------

REPOST_INST = False
PROXY = ''
INST_LOGIN = ''
INST_PASSWORD = ''

# -------------------------- Не разбираешься - не трогай! --------------------------

BASE_DIR = Path(__file__).parent
FILES_DIR = BASE_DIR.joinpath('files')
LOGS_DIR = BASE_DIR.joinpath('logs')

PROXY = PROXY or None
VK_ACCESS_TOKEN = VK_ACCESS_TOKEN or None

paths = [
    FILES_DIR,
    LOGS_DIR,
]

for path in paths:
    path.mkdir(exist_ok=True)
