# #439764 双向趋势追踪-Renko-交易策略Dual-direction-Trend-Tracking-Renko-Trading-Strategy -> `fmz_439764_vdub_supertrend_flip_f1_p1`

- FMZ source id: 439764 (lineage).
- Source: https://www.fmz.com/strategy/439764 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 15:50:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C124). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR band flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [1, 3] x `pd` [1, 10]: **4 trials**.

## Ambiguities resolved

- Exits on unused ids never sent. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
