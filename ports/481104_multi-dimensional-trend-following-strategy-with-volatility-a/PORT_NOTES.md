# #481104 Multi Dimensional Trend Following Strategy with Volatility Adaptive Stop Loss -> `fmz_481104_supertrend14x3_rsi65_sma50_long`

- FMZ source id: 481104 (lineage).
- Source: https://www.fmz.com/strategy/481104 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-08 15:12:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C241). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ratchet stop described (pending) |
| 2 | PASS | SuperTrend with RSI and SMA filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin 100 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `ma_length` [50, 100]: **4 trials**; ATR 14, RSI 14 / 65; the ratchet stop pending.

## Ambiguities resolved

- The ATR ratchet stop is kept pending (trailing_stop_pending). Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`
