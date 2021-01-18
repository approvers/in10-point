import base64
import logging
import os
import sys


from bot.client import DiscordClient
from db.firebase import FirebaseRealtimeDatabase

logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)s "
           "[\"%(name)s\":%(module)s:%(funcName)s():L%(lineno)d]: "
           "%(levelname)s \"%(message)s\"",
    stream=sys.stdout
)
logger = logging.getLogger()


def get_env(name):
    if name not in os.environ:
        logger.error(f"Environment variable '{name}' is not set, I can't continue this work.")
        return None
    return os.environ[name]


def main():
    firebase_credential = get_env("FIREBASE_CREDENTIAL")
    discord_token = get_env("DISCORD_TOKEN")
    init_message_channel = get_env("INIT_MESSAGE_CHANNEL")
    if firebase_credential is None or discord_token is None:
        logger.error("Some variable is not set; quiting.")
        return 1

    logger.debug("Creating Firebase Realtime Database Instance...")
    try:
        json_credential = base64.b64decode(firebase_credential.encode()).decode()
        firebase = FirebaseRealtimeDatabase(json_credential)
    except Exception as e:
        logger.error("'FIREBASE_CREDENTIAL' is not valid data! I can't read this, what the heck?")
        logger.exception(e)
        return 2

    bot_client = DiscordClient(firebase, init_message_channel)
    bot_client.run(discord_token)
    print("Discord bot ready!")


if __name__ == '__main__':
    sys.exit(main() or 0)
