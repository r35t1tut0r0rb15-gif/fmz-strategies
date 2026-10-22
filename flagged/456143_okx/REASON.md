# 配对交易策略OKX

- FMZ id: 456143
- Source: https://www.fmz.com/strategy/456143 (repository copy: `配对交易策略OKX.md`)
- Language: javascript
- Author: 小草
- Last modified (FMZ): 2024-07-11 11:29:05
- Kind: trading strategy/bot

## Why flagged (criterion 3: needs crypto-exchange-only features; found on reading, FMZ-C)

- Pairs grid on two OKX perpetual swaps (Pair_A / Pair_B .swap): it reads exchange positions, the OKX account equity (Info.data[0].totalEq) and contract values (CtVal), and sends iceberg limit orders off the live bid / ask in a timed loop, cancelling them each pass: crypto-exchange swap and account features, two instruments at once.

Not ported. Kept verbatim in `original_source.md` for future crypto-exchange work.
