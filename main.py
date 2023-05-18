import time
from threading import Thread

from reposter.tracking import TelegramTracker
from reposter.send import VkPoster, InstPoster
from reposter.database import get_new_posts, posted
from reposter.config import (
    CHANNEL,
    API_ID,
    API_HASH,
    PHONE,
    FILES_DIR,
    VK_ACCESS_TOKEN,
    VK_GROUP_ID,
    INST_LOGIN,
    INST_PASSWORD,
    PROXY,
    REPOST_VK,
    REPOST_INST,
)


tg_tracker = TelegramTracker(API_ID, API_HASH, CHANNEL, PHONE, FILES_DIR)

vk_poster = VkPoster(VK_ACCESS_TOKEN, VK_GROUP_ID, REPOST_VK)
inst_poster = InstPoster(INST_LOGIN, INST_PASSWORD, PROXY, REPOST_INST)


def post_handler():
    while True:
        posts = get_new_posts()
        for post in posts:
            vk_poster.send_post(post)
            inst_poster.send_post(post)
            posted(post.dir_path)
        time.sleep(10)


def main():
    Thread(target=post_handler, daemon=True).start()
    tg_tracker.start()


if __name__ == '__main__':
    main()
