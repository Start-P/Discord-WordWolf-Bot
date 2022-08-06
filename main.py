import discord
import random
import asyncio
from discord.ext import commands
from discord.ext import tasks

token = ''
activity = discord.Game(name=f"!help | start#2434 ")
bot = commands.Bot(command_prefix='!',
                   intents=discord.Intents.all(),
                   activity=activity,
                   status=discord.Status.do_not_disturb
                   )


VoteBool = False
voicechannel = False
alluser = []
wordlist = {"ringo": "better"}
wordwolf = ""
nowordwolf = []
guild = ""
votecounter = {}
voteduser = []
startchannel = ""


def reset():
    global VoteBool
    global voicechannel
    global alluser
    global wordwolf
    global nowordwolf
    global guild
    global votecounter
    global voteduser
    global startchannel
    VoteBool = voicechannel = alluser = wordwolf = nowordwolf = guild = votecounter = voteduser = startchannel = False


@bot.command()
async def start(ctx, times):  # times must be secounds
    global wordwolf
    global nowordwolf
    global voicechannel
    global votecounter
    global startchannel
    global VoteBool
    global guild
    global alluser
    if times.isdigit() == False:
        await ctx.reply(f'秒数は整数で指定してください。')
        return False
    # if int(times) <= 59:
    # await ctx.reply('少なくとも時間は60秒以上にしてください。')
    # return False
    if ctx.author.voice.channel == False:
        await ctx.reply('ボイスチャンネルに接続した状態で行ってください。')
        return False
    else:
        startchannel = ctx
        normalword = random.choice(list(wordlist.keys()))
        wolfword = wordlist[normalword]
        voicechannel = ctx.author.voice.channel
        alluser = [i.id for i in voicechannel.members]
        wordwolf = random.choice(voicechannel.members)
        nowordwolf = [i for i in voicechannel.members if i != wordwolf]
        votecounter = {user.name: 0 for user in voicechannel.members}
        guild = ctx.guild
        for user in nowordwolf:
            await user.send(f'{user.name}さんのワードは、{normalword}です。')
        await wordwolf.send(f"{wordwolf.name}さんのワードは、{wolfword}です。")
        await ctx.reply(f'全員にワードを送信しました。\n今から{times}秒間は議論をしてください。')
        await asyncio.sleep(int(times))
        await ctx.reply(f"議論をする時間が終了しました。怪しいと思ったユーザーに投票してください。")
        VoteBool = True
        return True


@bot.event
async def on_message(msg):
    global voteduser
    global votecounter
    channel = msg.channel
    if VoteBool and isinstance(channel,
                               discord.DMChannel) and msg.author.bot != True and msg.author.id not in voteduser:
        username = msg.content
        user = discord.utils.get(guild.members, name=username)
        print(user, votecounter, user.name)
        if user and user.name in votecounter.keys():
            votecounter[user.name] += 1
            await channel.send(f'{user.name}さんに投票しました。')
            voteduser.append(msg.author.id)
            return True
        else:
            await channel.send('ユーザーが存在しませんでした。')
    else:
        await bot.process_commands(msg)


@tasks.loop(seconds=1)
async def loop():
    print(alluser, voteduser)
    if VoteBool and set(voteduser) == set(alluser):
        print("aaaaaaaaa")
        result = ""
        sortedvotecounter = sorted(votecounter.items(), key=lambda x: x[0])
        guessedwordwolf = sortedvotecounter[0]
        for i in sortedvotecounter:
            result += f"{i[0]}さん：{i[-1]}票\n"
        if guessedwordwolf[0] == wordwolf.name:
            await startchannel.send(f"おめでとうございます！みなさんが投票した、{wordwolf.name}さんはワードウルフでした！")
        else:
            await startchannel.send(
                f"みなさんが投票した{guessedwordwolf[0]}さんは、\nワードウルフではありませんでした。ワードウルフは、{wordwolf.name}さんでした。")
        await startchannel.send(f'最終結果：\n```\n{result}\n```\nお疲れ様でした。')
        reset()


loop.start()
bot.run(token)
