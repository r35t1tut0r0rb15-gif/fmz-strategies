# #426626 K Trend Following Strategy Based on MA Candles and Supertrend -> `fmz_426626_ma_candle_supertrend_long`

- Source: https://www.fmz.com/strategy/426626 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-13 18:07:54). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [10, 20, 30] x `atr_length` [20, 30]: **6 trials**, defaults 20 / 30 (the source's); MA type rma, ATR mult 1, thresholds 0.2 / 0.7 fixed.

## Ambiguities resolved

- The '12M' [1] lookahead-on read is the previous calendar year of broker-day dates; the first data year has none, the second reads a partial year (data-start dependence, decision owed).
- allow_entry_in(long): long only; short signals only close longs, as the dir == -1 close does.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`
