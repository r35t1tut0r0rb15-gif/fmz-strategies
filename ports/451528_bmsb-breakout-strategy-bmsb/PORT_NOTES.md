# #451528 BMSB-Breakout-Strategy-BMSB-突破策略 -> `fmz_451528_bmsb_sma20_ema21_cross_reversal`

- FMZ source id: 451528 (lineage).
- Source: https://www.fmz.com/strategy/451528 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-15 16:40:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C186). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Support-band crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [20, 50] x `ema_len` [21, 50]: **4 trials**.

## Ambiguities resolved

- Later call wins a same-bar tie. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
