from threading import Thread

from reposter.send.vk import VkPoster
from reposter.tracking.telegram import TelegramTracker
from reposter.config import CHANNEL, API_ID, API_HASH, PHONE, FILES_DIR, VK_ACCESS_TOKEN, VK_GROUP_ID


tg_tracker = TelegramTracker(API_ID, API_HASH, CHANNEL, PHONE, FILES_DIR)
vk_poster = VkPoster(VK_ACCESS_TOKEN, VK_GROUP_ID)


def main():
    Thread(target=vk_poster.post_handler, daemon=True).start()
    tg_tracker.start()


if __name__ == '__main__':
    main()
