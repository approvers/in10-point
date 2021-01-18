import datetime
import logging
import re
import random
from typing import List

import discord

from db.firebase import FirebaseRealtimeDatabase
from db.model.in10_word import In10Word

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):
    SIN = [
        "例えば、`firebase.py`ですべてのModelのCRUDをやっています。",
        "例えば、コマンドの判定は愚直に`elif`をぐりぐり回してます。",
        "例えば、`In10Info`というModelがあります。伝わらない。",
        "例えば、メッセージが全部ハードコーディングされてます。認証情報とかはさすがに環境変数から読んでます。",
        "3時間で作ったので仕方がない。",
        "このメッセージのリストが`client.py`にあるのがすでにおかしい。"
    ]

    def __init__(self, db: FirebaseRealtimeDatabase, init_message_channel: int, **options):
        super().__init__(**options)
        self.db = db
        self.init_message_channel = init_message_channel
        self.words: List[In10Word] = []
        self.last_sync = datetime.datetime.now()

    async def on_ready(self):
        channel = await self.fetch_channel(self.init_message_channel)
        sent_message = await channel.send("🚀 `in10.json` を読み込んでいます。")
        self.sync()

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
        elif command[0] == "add":
            await self.add_word(channel, command[1:])
        elif command[0] == "check":
            await self.check_word(channel, command[1:])
        elif command[0] == "sync":
            await self.force_sync(channel)
        elif command[0] == "help":
            await self.help(channel)

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
        if in10_data is None:
            await channel.send("🤔 **WTF**: その人の淫獣ポイント情報がありません。たぶんまだ変なこと言ってないんだと思います。")
            return

        embed = discord.Embed(colour=0xff00ff, title=f"{in10_data.name} さんの淫獣ポイント")
        embed.add_field(name="淫獣ポイント", value=f"**{in10_data.point}** pt(s).", inline=True)
        embed.add_field(name="カウント回数", value=f"**{in10_data.count}** 回", inline=True)
        embed.add_field(name="平均ポイント", value=f"**{in10_data.point / in10_data.count}** pt/回", inline=False)
        await channel.send(embed=embed)

    async def add_word(self, channel: discord.TextChannel, command: List[str]):
        if len(command) < 1:
            await channel.send("💥 **犯すぞ**: 単語が必要です。")
            return

        word = command[0]
        weight = 0
        if len(command) > 1:
            if re.match(r"\d+\.\d+", command[1]) is not None:
                await channel.send("💥 **犯すぞ**: 第2引数は小数であってほしいです。")
                return
            weight = float(command[1])

        self.db.add_word(word, weight)
        self.sync()
        await channel.send(f"✅ {command[0]}、追加しました")

    async def check_word(self, channel: discord.TextChannel, command: List[str]):
        if len(command) < 1:
            await channel.send("💥 **犯すぞ**: 単語が必要です。")
            return

        found = list(filter(lambda x: x.word == command[0], self.words))
        if len(found) == 0:
            await channel.send(
                f"✨ ***CLEAR*** ✨\n**「{command[0]}」は使ってもカウントされません**。\n"
                f"「何故!?」となったら`in10/add {command[0]} [重み(任意)]` で追加できます。ぜひ。")
            return

        await channel.send(f"「{command[0]}」というと **{found[0].weight} pt(s).** 加算されます。")

    async def force_sync(self, channel:  discord.TextChannel):
        if datetime.datetime.now() - self.last_sync < datetime.timedelta(seconds=60):
            await channel.send("**ちょっと待ってください**: `sync`の実行は一定時間置く必要があります。")
            return
        self.sync()
        await channel.send(f"✅ 単語リストを†強制更新†しました。")

    async def help(self, channel: discord.TextChannel):
        await channel.send(
            "<:sasuin:759097700326703179> **`in10-point` | 淫獣ポイントBot**\n"
            "このサーバにいる人がどれくらい、どの程度変なこと言ったかを数値化して参照するためのBotです。\n"
            "```rank [制限: int]\n  淫獣ポイントのランキングを表示します。```"
            "```get <対象ユーザ: int/メンション>\n  特定のユーザの詳細情報を表示します。```"
            "```add <ワード: str> [重み: float]\n  新しく単語を追加します。```"
            "```check <ワード: str>\n  指定した言葉がアウトかどうかを表示します。淫獣ポイントには加算されません。```"
            "```\nsync\n  なんかの事情でFirebaseとこのBotの間で生じてしまった不整合をどうにかします。```"
            "```\nhelp\n  これです。```\n"
            f"免責事項: めんどくさくて設計をほぼ考えていません。{random.sample(DiscordClient.SIN, 1)[0]}\n"
            "そのうちリファクタするかもしれません。"
        )

    def sync(self):
        self.words = self.db.get_in10_words()
        self.last_sync = datetime.datetime.now()
        logger.info(f"{len(self.words)} word(s) loaded.")
