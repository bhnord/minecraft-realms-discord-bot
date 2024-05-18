import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
API_LOCATION = os.getenv("API_LOCATION")
DELAY = 60

help_command = commands.DefaultHelpCommand(no_category="Commands")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents,
                   help_command=help_command)


def getEndpoint(endpoint):
    return requests.get(API_LOCATION + endpoint)


async def setStatus():
    res = getEndpoint("/players")
    if res.status_code == 200:
        players = res.json()
        await bot.change_presence(
            activity=discord.CustomActivity(
                "🟢 {} players online".format(len(players["online"]))
            )
        )


async def job():
    while 1:
        await setStatus()
        await asyncio.sleep(DELAY)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected on Discord")

    # set up scheduler job
    print(f"setting status every {DELAY} seconds...")
    bot.loop.create_task(job())


@bot.command(name="online", help="Responds with the players currently online")
async def check_online(ctx):
    res = getEndpoint("/players")
    if res.status_code != 200:
        await ctx.send("an error occurred")
    else:
        players = res.json()

        msg = "```SaseCRAFT:\n--------------------\nOnline Players: {}  \
        \nTotal Players: {}\n--------------------```".format(
            players["online"], len(players["all_players"])
        )
        await ctx.send(msg)


if TOKEN:
    bot.run(TOKEN)
else:
    print("Missing Token")
