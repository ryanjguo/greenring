import sqlite3
import discord
import asyncio

async def get_ranking(ctx):
    conn = sqlite3.connect("stocks_transactions.db")
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT username, SUM(profit) AS total_profit
        FROM transactions
        WHERE action IN ('SELL', 'COVER')
        
        GROUP BY username
        ORDER BY total_profit DESC;
    """)

    profit_data = cursor.fetchall()
    conn.close()

    pages = []
    page_count = -(-len(profit_data) // 10)  # Calculate the number of pages
    for i in range(page_count):
        embed = discord.Embed(
            title=f"Profit Leaderboard for {ctx.guild.name}",
            colour=0x003399
        )
        embed.set_footer(
            text=f"Page {i + 1}/{page_count}"
        )
        for rank, (username, total_profit) in enumerate(profit_data[i * 10:i * 10 + 10], start=i * 10 + 1):
            embed.add_field(
                name=f"#{rank} {username}",
                value=f"Total Profit: {round(total_profit, 2)}%",
                inline=False
            )
        pages.append(embed)

    index = 0
    message = await ctx.send(embed=pages[0])
    emojis = ["◀️", "⏹", "▶️"]
    for emoji in emojis:
        await message.add_reaction(emoji)

    while not ctx.bot.is_closed():
        try:
            react, user = await ctx.bot.wait_for(
                "reaction_add",
                timeout=60.0,
                check=lambda r, u: r.emoji in emojis and u.id == ctx.author.id and r.message.id == message.id
            )
            if react.emoji == emojis[0] and index > 0:
                index -= 1
            elif react.emoji == emojis[1]:
                await message.delete()
                break
            elif react.emoji == emojis[2] and index < len(pages) - 1:
                index += 1

            await message.edit(embed=pages[index])
        except asyncio.TimeoutError:
            await message.delete()
            break