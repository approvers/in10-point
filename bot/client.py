import asyncio
import logging
import re
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
            logger.info(f"Command Smashed: {message.author.display_name}'{message.content}'")
            header_idx = message.content.index("/")
            await self.handle_command(message.channel, message.content[header_idx + 1:].split(" "))

        await self.handle_general_message(message.author, message.content)

    async def handle_general_message(self, author: discord.Member, content: str):
        add_point = 0
        add_count = 0
        for word in self.words:
            if word.word not in content:
                continue
            logger.info(f"{author.display_name}({author.id}) -> {str(word)}")
            add_point += word.weight
            add_count += 1

        if add_count == 0:
            return

        logger.info(f"{author.display_name}({author.id}) -> +{add_point} pt(s).")
        self.db.add_user_in10_point(author.id, author.name, add_point, add_count)

    async def handle_command(self, channel: discord.TextChannel, command: List[str]):
        if command[0] == "rank":
            await self.rank(channel, command[1:])
        elif command[0] == "get":
            await self.get_user_info(channel, command[1:])
        pass

    async def rank(self, channel: discord.TextChannel, command: List[str]):
        raw_limit = 10
        if len(command) > 0:
            if not command[0].isdigit():
                await channel.send("💥 **犯すぞ**: `rank`コマンドの第1引数は†非負の数値†である必要があります。")
                return
            raw_limit = int(command[0])
            if raw_limit == 0:
                await channel.send("💥 **犯すぞ**: http://scp-jp.wikidot.com/scp-240-jp")
                return

        msg = await channel.send("⏳ ちょっと待ってください、今Firebaseに淫獣ポイントについて聞いています")

        all_in10_info = self.db.get_all_in10_points()
        sorted_in10_info = list(sorted(all_in10_info, key=lambda x: x.point))
        stripped_in10_info = sorted_in10_info[:raw_limit]

        padding_length = len(str(raw_limit))
        content = "```asc\n"
        for i in range(len(stripped_in10_info)):
            in10_info = stripped_in10_info[i]
            content += f"#{str(i + 1).rjust(padding_length)}: {in10_info.name} " \
                      f"({in10_info.point}pt, {in10_info.count}回)\n"
        content += "```"

        await msg.edit(content=content)

    async def get_user_info(self, channel: discord.TextChannel, command: List[str]):
        if len(command) < 1:
            await channel.send("💥 **犯すぞ**: ユーザーIDかメンションが必要です。")
            return

        target_user_id = -1
        mention_match = re.match("<@!(\d+)>", command[0])
        if mention_match is not None:
            target_user_id = int(mention_match[1])
        elif command[0].isdigit():
            target_user_id = int(command[0])
        else:
            await channel.send("💥 **犯すぞ**: ユーザIDかメンションをください、どっちにも解釈できませんでした")
            return

        in10_data = self.db.get_user_in10_point(target_user_id)
        embed = discord.Embed(colour=0xff00ff, title=f"{in10_data.name} さんの淫獣ポイント")
        embed.add_field(name="淫獣ポイント", value=f"**{in10_data.point}** pt(s).", inline=True)
        embed.add_field(name="カウント回数", value=f"**{in10_data.count}** 回", inline=True)
        embed.add_field(name="平均ポイント", value=f"**{in10_data.point / in10_data.count}** pt/回", inline=False)
        await channel.send(embed=embed)



