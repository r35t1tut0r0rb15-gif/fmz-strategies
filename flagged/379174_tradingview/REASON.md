# TradingView策略信号下单机器人-币安版

- FMZ id: 379174
- Source: https://www.fmz.com/strategy/379174 (repository copy: `TradingView策略信号下单机器人-币安版.md`)
- Language: javascript
- Author: 高频量化
- Last modified (FMZ): 2022-08-23 10:25:06
- Kind: trading strategy/bot

## Why flagged (criterion 3: needs crypto-exchange-only features)

- funding rate
- multiple exchanges (cross-exchange arbitrage/hedge)
- perpetual/dated crypto contract
- exchange leverage/margin setting
- best bid/ask from ticker

## Other screening notes

- Criterion 1: FAIL - tick/order-level loop with no bar data (no GetRecords/indicators)
- Duplicate group: 379174

Not ported. Kept verbatim in `original_source.md` for future crypto-exchange work.
