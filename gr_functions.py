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
        self.status = "OPEN"
        self.profit = 0

    def to_embed(self):
        if self.profit == 0:
            embed_color = 0xFFFFFF
        elif self.profit > 0:
            embed_color = 0x00FF00
        else:
            embed_color = 0xFF0000

        embed = discord.Embed(
            title=f"{self.action.capitalize()} {self.ticker.upper()}",
            description="Transaction was successfully stored.",
            color=embed_color,
        )
        embed.set_author(name=self.user.name, icon_url=self.user.avatar.url)
        embed.add_field(name="User", value=self.user, inline=True)
        embed.add_field(name="Ticker", value=self.ticker.upper(), inline=True)
        embed.add_field(name="Price", value=self.price, inline=True)
        embed.add_field(name="Status", value=self.status, inline=True)
        if self.action == "SELL" or self.action == "COVER":
            embed.add_field(name="Profit", value=f'{str(self.profit)}%')
        embed.add_field(name="Date", value=self.datetime)
        # embed.set_footer(text=f"{self.date} EST")
        return embed
    
    def updated_trade_embed(self, prev_price, prev_date, avg_price):
        if self.profit == 0:
            embed_color = 0xFFFFFF
        elif self.profit > 0:
            embed_color = 0x00FF00
        else:
            embed_color = 0xFF0000
        embed = discord.Embed(
            title=f"Updated {self.action.capitalize()} {self.ticker.upper()}",
            description=f"You have previously opened a trade for {self.ticker.upper()} at",
            color=embed_color,
        )
        embed.set_author(name=self.user.name, icon_url=self.user.avatar.url)
        embed.add_field(name="Previous Price", value=prev_price, inline=True)
        embed.add_field(name="Previous Date", value=prev_date, inline=True)
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="Current Price", value=self.price, inline=True)
        embed.add_field(name="Current Date", value=self.datetime, inline=True)
        embed.add_field(name="Averaged Price", value=f"Thus your price is averaged to {avg_price}\n", inline=False)
        embed.add_field(name="User", value=self.user, inline=True)
        embed.add_field(name="Ticker", value=self.ticker.upper(), inline=True)
        embed.add_field(name="Status", value=self.status, inline=True)
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
        print(stock.info)

        if info["exchange"] in [
            "NCM",
            "NGM",
            "NMS",
            "NYQ",
            "ASE",
            "NGM",
            "PCX",
            "TOR",
            "VAN",
            "CNQ",
            "NEO",
            "BTS",
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


def open_trade(action, ticker, message):
    # SQL Query for all open transaction by same user and ticker'
    conn = sqlite3.connect("stocks_transactions.db")
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT * 
    FROM transactions 
    WHERE status = 'OPEN' AND ticker = ? AND action = ?
    ORDER BY date DESC
    LIMIT 1;
        """,
        (ticker, action),
    )
    result = cursor.fetchone()
    # Check if a result was found
    if result is None:
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
        cursor.execute(
            """
            INSERT INTO transactions (username, action, ticker, price, date, status) VALUES (?, ?, ?, ?, ?, ?)
        """,
            (message.author.name, action, ticker, market_price, current_datetime, "OPEN"),
        )
        conn.commit()
        conn.close()
        return new_transaction.to_embed()
    else:
        # Update open trade
        curr_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        curr_price = round(getCurrentPrice(ticker), 2)
        avg_price = round((curr_price + result[4]) / 2, 2)

        # Update old transaction to status = 'UPDATED'
        cursor.execute(
            """
            UPDATE transactions
            SET status = 'UPDATED'
            WHERE id = ?
            """, (result[0],)
        )

        # Log new transaction of BUY/SHORT
        cursor.execute(
            """
            INSERT INTO transactions (username, action, ticker, price, date, status) VALUES (?, ?, ?, ?, ?, ?)
        """,
            (message.author.name, action, ticker, avg_price, curr_date, "OPEN"),
        )

        conn.commit()
        conn.close()
        updated_transaction = Transaction(message.author, action, ticker, curr_price, curr_date)
        return updated_transaction.updated_trade_embed(result[4], result[5], avg_price)
        

def close_trade(action, ticker, message):
    # SQL Query for all open transaction by same user and ticker
    if action == "SELL":
        oppo_action = "BUY"
    else:
        oppo_action = "SHORT"

    conn = sqlite3.connect("stocks_transactions.db")
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT * 
    FROM transactions 
    WHERE status = 'OPEN' AND ticker = ? AND action = ? AND username = ?
    ORDER BY date DESC
    LIMIT 1;
        """,
        (ticker, oppo_action, message.author.name),
    )

    result = cursor.fetchone()
    # Check if a result was found
    if result is not None:
        # Same values
        id = result[0]
        username = result[1]
        ticker = result[3]

        # New values
        price = round(getCurrentPrice(ticker), 2)
        profit = round((price - result[4]) / result[4] * 100, 2)  # (Bought(shorted) price - Sold(covered) price) / bought(shorted) price * 100
        if action == "COVER":
            profit = -profit
        status = "CLOSED"
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current time as of EST

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
        sold_transaction = Transaction(message.author, action, ticker, price, date)
        sold_transaction.profit = profit
        sold_transaction.status = status
        return sold_transaction.to_embed() # CREATE A NEW EMBED FOR SOLD TRANSACTIONS
    else:
        # ERROR: No open trades to sell
        return embed_error(0)
