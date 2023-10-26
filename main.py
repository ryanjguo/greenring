# Import Statements
import discord
from datetime import datetime
from discord.ext import commands
from gr_functions import *
import yfinance as yf
from gr_functions import Transaction
import sqlite3

TOKEN = "MTA3ODY4ODEzODg5NTAzNjU2Nw.GUAvXA.zkq70yUu0u-p9Z0lFxHrFt6AgpcNYb7sJXDRr4"

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
async def hello(ctx):
    """Simple command to respond with 'Hello!'."""
    await ctx.send("Hello!")


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

        if checkMarketOpen() == False:
            await message.channel.send(
                "Market is closed. Please try again at another time."
            )
            return

        if action == "BUY" or action == "SHORT":
            # Check market price and date/time
            market_price = round(getCurrentPrice(ticker), 2)
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create transaction object
            new_transaction = Transaction(
                message.author, action, ticker, market_price, current_datetime
            )

            # Add market price and date/time to transaction object
            new_transaction.price = market_price
            new_transaction.date = current_datetime

            # Store transaction object in database
            conn = sqlite3.connect("stocks_transactions.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO transactions (username, action, ticker, price, date) VALUES (?, ?, ?, ?, ?)
            """,
                (message.author.name, action, ticker, market_price, current_datetime),
            )
            conn.commit()
            conn.close()

            ## CHECK IF ACTION IS A CLOSE TRADE (SELL OR COVER)

            # Display transaction object in chat
            await message.channel.send(embed=new_transaction.to_embed())
        else:  # action == 'SELL' or action == 'COVER'
            await message.channel.send(embed=close_trade(action, ticker, message))

    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(TOKEN)
