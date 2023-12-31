# Import Statements
import discord
from datetime import datetime
from discord.ext import commands
from gr_functions import *
import yfinance as yf
import sqlite3
from gr_ranking import *
import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)

TOKEN = config["token"]

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

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
    await get_ranking(ctx)


@bot.event
async def on_message(message):
    """Event for handling messages."""
    # If the message is from the bot itself, ignore it
    if message.author == bot.user:
        return

    string_content = message.content.lower().split()

    if len(string_content) == 3:

        result = unpack_message(message)

        if result is None:
            return
        
        action, ticker = unpack_message(message)
        price = string_content[2]

        if checkTickerExists(ticker) == False:
            await message.channel.send("Invalid ticker. Please try again.")
            return

        if checkMarketOpen() == True:
            await message.channel.send(
                "Market is open. The bot will automatically retrieve the current market price.\nE.g. 'buy AAPL' or 'cover AMZN'"
            )
            return

        if action == "BUY" or action == "SHORT":
            await message.channel.send(embed=open_trade(action, ticker, message, price))
        else:
            await message.channel.send(
                embed=close_trade(action, ticker, message, price)
            )

    if len(string_content) == 2:
        result = unpack_message(message)

        if result is None:
            return

        action, ticker = unpack_message(message)

        if checkTickerExists(ticker) == False:
            await message.channel.send("Invalid ticker. Please try again.")
            return

        # User should specify price when market is closed, return error if not
        if checkMarketOpen() == False:
            await message.channel.send(
                "Market is closed. Please specify a price for your trade.\nE.g. 'buy AAPL 100' or 'cover AMZN 250'"
            )
            return
        else:
            # If market is open, retrieve current market price
            price = getCurrentPrice(ticker)

        if action == "BUY" or action == "SHORT":  # action == 'BUY' or action == 'SHORT'
            # Display transaction object in chat
            await message.channel.send(embed=open_trade(action, ticker, message, price))
        else:  # action == 'SELL' or action == 'COVER'
            await message.channel.send(
                embed=close_trade(action, ticker, message, price)
            )

    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(TOKEN)
