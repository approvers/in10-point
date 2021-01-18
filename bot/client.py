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

        if message.content.startswith("in10/") or message.content.startswith("i0/"):
            header_idx = message.content.index("/")
            await self.handle_command(message.channel, message.content[header_idx + 1:].split(" "))

        await self.handle_general_message(message.author, message.content)

    async def handle_general_message(self, author: discord.Member, content: str):
        add_point = 0
        for word in self.words:
            if word.word not in content:
                continue
            logger.info(f"{author.display_name}({author.id}) -> {str(word)}")
            add_point += word.weight

        if add_point == 0:
            return

        logger.info(f"{author.display_name}({author.id}) -> +{add_point} pt(s).")


    async def handle_command(self, channel: discord.TextChannel, command: List[str]):
        pass



