# Bybit-算法接针-VWAP-BTC

- FMZ id: 182656
- Source: https://www.fmz.com/strategy/182656 (repository copy: `Bybit-算法接针-VWAP-BTC.md`)
- Language: javascript
- Author: 扁豆子
- Last modified (FMZ): 2021-01-29 10:44:37
- Kind: trading strategy/bot

## Why flagged (criterion 3: needs crypto-exchange-only features; found on reading, FMZ-C)

- The entries are triggered by BitMEX's liquidation websocket feed (XBTUSD liquidations over 250,000 contracts) with a Bybit swap account: crypto-exchange-only data the project's bars do not carry.

Not ported. Kept verbatim in `original_source.md` for future crypto-exchange work.
