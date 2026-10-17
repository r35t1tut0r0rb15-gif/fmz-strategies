# 移动平均数RSI相关性加密货币趋势策略Moving-Average-RSI-Crypto-Correlation-Trend-Strategy

- FMZ id: 435081
- Source: https://www.fmz.com/strategy/435081 (repository copy: `移动平均数RSI相关性加密货币趋势策略Moving-Average-RSI-Crypto-Correlation-Trend-Strategy.md`)
- Language: PineScript
- Author: ChaoZhang
- Last modified (FMZ): 2023-12-12 10:26:21
- Kind: trading strategy/bot

## Why flagged (criterion 3: needs crypto-exchange-only features; found on reading, FMZ-C)

- The signals are computed on request.security('BTC_USDT:swap', timeframe.period, close / open / high / low) with correlation candles on by default: a crypto-exchange perpetual contract used as the signal source for the chart symbol (as #430742).

Not ported. Kept verbatim in `original_source.md` for future crypto-exchange work.
