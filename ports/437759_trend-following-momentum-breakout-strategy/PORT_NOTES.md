# #437759 Trend Following Momentum Breakout Strategy -> `fmz_437759_noro_supertrend_pullback`

- FMZ source id: 437759 (lineage).
- Source: https://www.fmz.com/strategy/437759 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-05 13:38:18). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C105). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR SuperTrend side and candle colour |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based lot and capital % stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atr_len` [7, 14]: **4 trials**.

## Ambiguities resolved

- The script's SuperTrend recursion as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
