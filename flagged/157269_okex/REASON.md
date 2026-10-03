# OKEX期现对冲

- FMZ id: 157269
- Source: https://www.fmz.com/strategy/157269 (repository copy: `OKEX期现对冲.md`)
- Language: javascript
- Author: larry_super
- Last modified (FMZ): 2019-07-16 14:06:39
- Kind: trading strategy/bot

## Why flagged (criterion 3: needs crypto-exchange-only features)

- order book (depth) used
- multiple exchanges (cross-exchange arbitrage/hedge)
- arbitrage/hedging between contracts or venues
- exchange leverage/margin setting

## Other screening notes

- Criterion 1: FAIL - tick/order-level loop with no bar data (no GetRecords/indicators)
- Duplicate group: none

Not ported. Kept verbatim in `original_source.md` for future crypto-exchange work.
