import asyncio
import logging
from typing import List

import discord

from db.firebase import FirebaseRealtimeDatabase
from db.model.in10_word import In10Word

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):
    def __init__(self, db: FirebaseRealtimeDatabase, init_message_channel: int, **options):
        super().__init__(**options)
        self.db = db
        self.init_message_channel = init_message_channel
        self.words: List[In10Word] = []

    async def on_ready(self):
        channel = await self.fetch_channel(self.init_message_channel)
        sent_message = await channel.send("🚀 `in10.json` を読み込んでいます。")

        self.words = self.db.get_in10_words()
        logger.info("Discord bot has been initialized successfully.")
        logger.info(f"{len(self.words)} word(s) loaded.")

        await sent_message.edit(content="🚀 準備完了です！")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return


