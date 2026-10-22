# #445814 布林带EMA趋势跟踪策略Bollinger-Bands-EMA-Trend-Following-Strategy -> `fmz_445814_upper_band_above_ema100_breakout_reversal`

- FMZ source id: 445814 (lineage).
- Source: https://www.fmz.com/strategy/445814 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-22 14:27:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C173). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band breakout above an EMA, band / EMA breakdowns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [50, 20] x `ema_len` [100, 200]: **4 trials**; the width fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
