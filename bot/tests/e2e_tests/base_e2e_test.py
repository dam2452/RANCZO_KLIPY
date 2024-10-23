import logging
import time
from typing import Optional

from telethon.sync import TelegramClient
from telethon.tl.custom.message import Message

from bot.tests.e2e_tests.settings import settings as s

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseE2ETest:
    client: Optional[TelegramClient] = None

    @classmethod
    def setup_class(cls) -> None:
        if s.SESSION:
            cls.client = TelegramClient(s.SESSION, s.API_ID, s.API_HASH)
            logger.info('Klient Telegram został utworzony z sesją.')
        else:
            cls.client = TelegramClient('test_session', s.API_ID, s.API_HASH)
        cls.client.start(password=s.PASSWORD, phone=s.PHONE)
        logger.info('Klient Telegram został uruchomiony.')

    @classmethod
    def teardown_class(cls) -> None:
        cls.client.disconnect()
        logger.info('Klient Telegram został rozłączony.')

    def send_command(self, command_text: str) -> Message:
        sent_message = self.client.send_message(s.BOT_USERNAME, command_text)
        sent_message_id = sent_message.id

        time.sleep(2)

        messages = self.client.iter_messages(
            s.BOT_USERNAME,
            min_id=sent_message_id,
            reverse=True,
        )

        for message in messages:
            if message.out:
                continue
            if message.id <= sent_message_id:
                continue
            print(f'Odpowiedź bota: {message.text}')
            return message
        raise ValueError("Bot nie odpowiedział na komendę.")

def main():
    BaseE2ETest.setup_class()
    test = BaseE2ETest()
    test.send_command("test")
    print("main")

if __name__ == "__main__":
    main()
