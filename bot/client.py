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
        self.words = self.db.get_in10_words()
        logging.info("Discord bot has been initialized successfully.")
        logger.info(f"{len(self.words)} word(s) loaded.")

        channel = await self.fetch_channel(self.init_message_channel)
        await channel.send("🚀 In10-point is ready!")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
