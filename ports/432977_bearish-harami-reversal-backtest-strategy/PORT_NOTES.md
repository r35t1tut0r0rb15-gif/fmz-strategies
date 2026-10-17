# #432977 Bearish Harami Reversal Backtest Strategy -> `fmz_432977_bearish_harami_short`

- FMZ source id: 432977 (lineage).
- Source: https://www.fmz.com/strategy/432977 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-23 11:47:10). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C56). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked level exits |
| 2 | ADAPT | Price-unit distances -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND432977. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.33, 1.0] x `sl_atr` [0.17, 0.5]: **4 trials**; body_atr 0.05 and ATR 14 fixed.

## Ambiguities resolved

- Price-unit distances as ATR multiples (criterion 2 ADAPT); the level resets are close-checked exit signals. Short only. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
