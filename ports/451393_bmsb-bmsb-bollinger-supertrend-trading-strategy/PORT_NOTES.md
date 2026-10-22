# #451393 BMSB-布林麦克超级趋势交易策略-BMSB-Bollinger-SuperTrend-Trading-Strategy -> `fmz_451393_bmsb_band_break_reversal`

- FMZ source id: 451393 (lineage).
- Source: https://www.fmz.com/strategy/451393 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-14 15:52:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C184). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Support-band breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [20, 50] x `ema_len` [21, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "6h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
