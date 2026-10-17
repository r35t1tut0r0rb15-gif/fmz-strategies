# 相对强弱指数多空策略Relative-Strength-Index-Long-Short-Strategy

- FMZ id: 432350
- Source: https://www.fmz.com/strategy/432350 (repository copy: `相对强弱指数多空策略Relative-Strength-Index-Long-Short-Strategy.md`)
- Language: PineScript
- Author: ChaoZhang
- Last modified (FMZ): 2023-11-16 17:06:14
- Kind: trading strategy/bot

## Why flagged (criterion 3: needs crypto-exchange-only features; found on reading, FMZ-C)

- The signal is the RSI of request.security('CRYPTOCAP:TOTAL2', '120', close[1]) (a crypto market-cap index) divided by the chart's RSI: the strategy needs crypto-market index data that the project's single-symbol bars do not carry (as #430742).

Not ported. Kept verbatim in `original_source.md` for future crypto-exchange work.
