# Greenring Discord Bot 🤖

## Commands
### Open/Close Trades 📈
Trades can be made both during market hours or before/after market hours.

Accepted formats of actions include:
- Buy, bot, bought
- sell, sold, sel, close
- short, shorted
- cover, covered

_During Market Hours:_  
All commands should follow the form _**[Action] [Symbol]**_  
For example: Buy AAPL, Sell AMZN  
The bot will automatically retrieve the live price of the stock, and return a Discord embed acknowledging your trade.

<img width="355" alt="image-during-market-hours" src="https://github.com/ryanjguo/greenring/assets/88060249/2c8c0b40-b1b7-412b-9795-3b113f983b5a">

_Before/After Market Hours:_ 
All commands should follow the form _**[Action] [Symbol] [Price]**_  
For example: Buy AAPL 123.45, Sell AMZN 159.12  

<img width="325" alt="image-after-market-hours" src="https://github.com/ryanjguo/greenring/assets/88060249/d949326e-be6c-4faa-863f-73e75da09e6c">

Note: If you buy with a trade open already, it will update your trade by averaging the prices.

<img width="357" alt="image-updated-trade" src="https://github.com/ryanjguo/greenring/assets/88060249/c141a7d2-657c-422c-a9db-44429a3983e7">

### !getrank 🥇

This feature returns a Discord Embed of the top-ranking users by their profit, for the duration of all time (starting from January 1st, 2024). Users can scroll through pages by reacting with the emojis below the embed. 


If you find any issues with the bot or have any suggestions, please ping/DM me on Discord, _**@rgld**_, or any of the staff team. 
