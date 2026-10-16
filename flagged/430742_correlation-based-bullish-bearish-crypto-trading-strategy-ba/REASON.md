# 基于华尔街捕鼠光环指标的加密货币看涨看跌策略Correlation-based-Bullish-Bearish-Crypto-Trading-Strategy-Based-on-Wall-Street-CCI-Index

- FMZ id: 430742
- Source: https://www.fmz.com/strategy/430742 (repository copy: `基于华尔街捕鼠光环指标的加密货币看涨看跌策略Correlation-based-Bullish-Bearish-Crypto-Trading-Strategy-Based-on-Wall-Street-CCI-Index.md`)
- Language: PineScript
- Author: ChaoZhang
- Last modified (FMZ): 2023-11-01 11:27:20
- Kind: trading strategy/bot

## Why flagged (criterion 3: needs crypto-exchange-only features; found on reading, FMZ-C)

- The signal is a WMA 200 of request.security('BTC_USDT:swap', timeframe.period, hlc3): a crypto-exchange perpetual contract used as the signal source for the chart symbol, which the project's single-symbol bars do not carry (as #426832).

Not ported. Kept verbatim in `original_source.md` for future crypto-exchange work.
