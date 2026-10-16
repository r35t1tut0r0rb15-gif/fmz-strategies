# #430164 动态K线方向策略Dynamic-Candle-Direction-Strategy -> `fmz_430164_candle_counter`

- FMZ source id: 430164 (lineage).
- Source: https://www.fmz.com/strategy/430164 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-25 16:57:05). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | The price-unit doji test -> an ATR fraction. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | A fixed quantity of 1 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`num_candles` [7, 4] x `doji_atr` [0.002, 0.05]: **4 trials**; ATR 14 fixed.

## Ambiguities resolved

- Price-unit doji test -> doji_atr x ATR(14). REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
