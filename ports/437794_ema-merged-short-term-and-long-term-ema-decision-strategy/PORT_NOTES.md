# #437794 短期长期EMA决策合并策略Merged-Short-Term-and-Long-Term-EMA-Decision-Strategy -> `fmz_437794_ema3_30_difference_band`

- FMZ source id: 437794 (lineage).
- Source: https://www.fmz.com/strategy/437794 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-05 16:07:58). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C106). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit threshold -> fraction of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`thr_frac` [1.2e-08, 0.001] x `slow` [30, 50]: **4 trials**; EMA 3 fixed.

## Ambiguities resolved

- Price-unit threshold -> fraction of the close (reading and a real band). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
