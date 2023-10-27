# Import Statements
import discord
from datetime import datetime
from discord.ext import commands
from gr_functions import *
import yfinance as yf
from gr_functions import Transaction
import sqlite3
from gr_ranking import *
import json

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

TOKEN = config['token']

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

bot_words = ("bot ", "bought ", "buy ")
sell_words = ("sell ", "sold ", "sel ", "close ")
short_words = ("short ", "shorted ")
cover_words = ("cover ", "covered ")

init_db()


@bot.event
async def on_ready():
    print(f"Bot is logged in as {bot.user.name} - {bot.user.id}")
    print("------")


@bot.command()
async def hello(ctx, arg=""):
    """Simple command to respond with 'Hello!'."""
    await ctx.send(f"Hello {arg}!")

@bot.command()
async def getrank(ctx):
    print("hello world")
    await get_ranking(ctx)

@bot.event
async def on_message(message):
    """Event for handling messages."""
    # If the message is from the bot itself, ignore it
    if message.author == bot.user:
        return

    string_content = message.content.upper().split()

    if len(string_content) == 2:
        ticker = string_content[1]

        action = None
        if message.content.startswith(bot_words):
            action = "BUY"
        elif message.content.startswith(sell_words):
            action = "SELL"
        elif message.content.startswith(short_words):
            action = "SHORT"
        elif message.content.startswith(cover_words):
            action = "COVER"
        else:
            return

        if checkTickerExists(ticker) == False:
            await message.channel.send("Invalid ticker. Please try again.")
            return

        # For testing purposes
        if checkMarketOpen() == False:
            await message.channel.send(
                "Market is closed. Please try again at another time."
            )
            return

        if action == "BUY" or action == "SHORT":
            ## CHECK IF ACTION IS A CLOSE TRADE (SELL OR COVER)

            # Display transaction object in chat
            await message.channel.send(embed=open_trade(action, ticker, message))
        else:  # action == 'SELL' or action == 'COVER'
            await message.channel.send(embed=close_trade(action, ticker, message))

    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(TOKEN)
