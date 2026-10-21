# #437508 KP移动平均趋势策略Heyping-Moving-Average-Trend-Strategy -> `fmz_437508_weekly_close_ema_cross_long`

- FMZ source id: 437508 (lineage).
- Source: https://www.fmz.com/strategy/437508 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-03 12:18:29). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C101). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly values from completed weeks |
| 2 | PASS | Average crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fama` [10, 5] x `sloma` [100, 50]: **4 trials**; the W / D frames fixed.

## Ambiguities resolved

- Weekly close = the last completed broker week's; plain closes. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
