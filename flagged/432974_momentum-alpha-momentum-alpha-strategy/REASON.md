# Momentum-Alpha策略Momentum-Alpha-Strategy

- FMZ id: 432974
- Source: https://www.fmz.com/strategy/432974 (repository copy: `Momentum-Alpha策略Momentum-Alpha-Strategy.md`)
- Language: PineScript
- Author: ChaoZhang
- Last modified (FMZ): 2023-11-23 11:34:40
- Kind: trading strategy/bot

## Why flagged (criterion 3: needs crypto-exchange-only features; found on reading, FMZ-C)

- The alpha and beta are measured against request.security('BTC_USDT:swap', timeframe.period, close), a crypto-exchange perpetual contract used as the benchmark for the chart symbol: the strategy needs a second, crypto-exchange instrument that the project's single-symbol bars do not carry (as #430742).

Not ported. Kept verbatim in `original_source.md` for future crypto-exchange work.
