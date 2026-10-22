# 比特币期货头寸智能交易策略Bitcoin-Futures-Position-Trading-Strategy

- FMZ id: 440084
- Source: https://www.fmz.com/strategy/440084 (repository copy: `比特币期货头寸智能交易策略Bitcoin-Futures-Position-Trading-Strategy.md`)
- Language: PineScript
- Author: ChaoZhang
- Last modified (FMZ): 2024-01-26 15:01:24
- Kind: trading strategy/bot

## Why flagged (criterion 3: needs crypto-exchange-only features; found on reading, FMZ-C)

- Every signal is the RSI 7 of request.security('BTC_USDT:swap', '', open): a crypto-exchange perpetual contract used as the signal source for the chart symbol (as #430742).

Not ported. Kept verbatim in `original_source.md` for future crypto-exchange work.
