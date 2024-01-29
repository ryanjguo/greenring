# Greenring Discord Bot 🤖
## 指令
### 开启/关闭交易 📈
交易可以在市场交易时间内进行，也可以在市场交易时间之前/之后进行。

接受的操作格式包括：
- Buy, bot, bought
- sell, sold, sel, close
- short, shorted
- cover, covered
  
_市场交易时间内:_  
所有指令应遵循 [操作] [股票代码] 的形式  
例如：Buy AAPL，Sell AMZN  
机器人将自动获取股票的实时价格，并返回一个 Discord 嵌入以确认您的交易。

<img width="355" alt="image-during-market-hours" src="https://github.com/ryanjguo/greenring/assets/88060249/2c8c0b40-b1b7-412b-9795-3b113f983b5a">  

_市场交易时间之前/之后:_  
所有指令应遵循 [操作] [股票代码] [价格] 的形式  
例如：Buy AAPL 123.45，Sell AMZN 159.12  

<img width="325" alt="image-after-market-hours" src="https://github.com/ryanjguo/greenring/assets/88060249/d949326e-be6c-4faa-863f-73e75da09e6c">  

注：如果您在已经开启的交易中买入，它将通过平均价格来更新您的交易。

<img width="357" alt="image-updated-trade" src="https://github.com/ryanjguo/greenring/assets/88060249/c141a7d2-657c-422c-a9db-44429a3983e7">  

## !getrank 🥇
此功能返回一个 Discord 嵌入，显示按利润排名的前几位用户，统计从2024年1月1日开始的所有时间。用户可以通过对嵌入下方的表情符号进行反应来滚动页面。

如果您发现机器人存在任何问题或有任何建议，请在 Discord 上 @rgld我，或与任何工作人员联系。
