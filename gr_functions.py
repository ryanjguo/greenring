import yfinance as yf
import discord
import sqlite3
import random
import datetime
import pytz


def init_db():
    conn = sqlite3.connect("stocks_transactions.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            ticker TEXT NOT NULL,
            price REAL NOT NULL,
            date TEXT NOT NULL,
            profit REAL, 
            status TEXT NOT NULL DEFAULT 'OPEN'
        )
    """  # PROFIT ONLY FOR SELL AND COVER
    )  # STATUS: OPEN, CLOSED, UPDATED
    conn.commit()
    conn.close()


class Transaction:
    def __init__(self, user, action, ticker, price, datetime):
        self.user = user
        self.action = action
        self.ticker = ticker
        self.price = price
        self.datetime = datetime

    def to_embed(self):
        random_color = random.randint(0, 0xFFFFFF)
        embed = discord.Embed(
            title=f"{self.action.capitalize()} {self.ticker.upper()}",
            description="Transaction was successfully stored.",
            color=random_color,
        )
        embed.set_author(name=self.user.name, icon_url=self.user.avatar.url)
        embed.add_field(name="User", value=self.user, inline=True)
        embed.add_field(name="Ticker", value=self.ticker.upper(), inline=True)
        embed.add_field(name="Price", value=self.price, inline=True)
        embed.add_field(name="Date", value=self.datetime)
        # embed.set_footer(text=f"{self.date} EST")
        return embed


def embed_error(err_num):
    error_list = ["You have no open trades for you to sell."]

    embed = discord.Embed(
        title="There was an error with your request.",
        description=error_list[err_num],
        color=0xFF0000,
    )
    return embed


def checkTickerExists(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if info["exchange"] in [
            "NMS",
            "NYQ",
            "ASE",
            "NGM",
            "PCX",
            "TOR",
            "VAN",
            "CNQ",
            "NEO",
        ]:
            return True
        else:
            return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def checkMarketOpen():
    # Set the time zone to Eastern Standard Time (EST)
    est = pytz.timezone("US/Eastern")

    # Get the current date and time in EST
    current_time = datetime.datetime.now(est)

    # Define the start and end times
    start_time = est.localize(
        datetime.datetime(
            current_time.year, current_time.month, current_time.day, 9, 30, 0
        )
    )
    end_time = est.localize(
        datetime.datetime(
            current_time.year, current_time.month, current_time.day, 16, 0, 0
        )
    )

    # Check if the current time is within the specified range
    if start_time <= current_time <= end_time:
        return True
    else:
        return False


def getCurrentPrice(ticker):
    yf_ticker = yf.Ticker(ticker)
    todays_data = yf_ticker.history(period="1d")
    return todays_data["Close"][0]


def close_trade(action, ticker):
    # SQL Query for all open transaction by same user and ticker
    conn = sqlite3.connect("stocks_transactions.db")
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT * 
    FROM transactions 
    WHERE status = 'OPEN' AND ticker = ?
    ORDER BY date_opened DESC
    LIMIT 1;
        """,
        (ticker,),
    )

    result = cursor.fetchone()
    # Check if a result was found
    if result is not None:
        # Same values
        id = result[0]
        username = result[1]
        ticker = result[3]

        # New values
        price = getCurrentPrice(ticker)
        profit = price / result[4] * 100  # Sold(covered) price / bought(shorted) price * 100
        status = "CLOSED"
        date = datetime.datetime.now(pytz.timezone("US/Eastern"))  # Current time as of EST

        # Update the old transaction to be closed
        cursor.execute(
            """
            UPDATE transactions
            SET status = 'CLOSED'
            WHERE id = ?
        """,
            (id,),
        )

        # Log new transaction of SELL/COVER
        cursor.execute(
            """
            INSERT INTO transactions (username, action, ticker, price, date, profit, status) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (username, action, ticker, price, date, profit, status),
        )

        # Commit changes and close connection
        conn.commit()
        conn.close()
    else:
        # ERROR: No open trades to sell
        return embed_error(0)
