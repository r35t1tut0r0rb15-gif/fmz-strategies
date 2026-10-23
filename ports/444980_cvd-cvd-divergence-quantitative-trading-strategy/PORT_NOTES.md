# #444980 CVD背离量化交易策略CVD-Divergence-Quantitative-Trading-Strategy -> `fmz_444980_cvd_pivot_divergence_pct_bracket_reversal`

- FMZ source id: 444980 (lineage).
- Source: https://www.fmz.com/strategy/444980 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-15 16:47:47). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed 5 % / 10 % bracket from the fill |
| 2 | PASS | Price / cumulative-volume-delta pivot divergences |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lb_left` [7, 5] x `lb_right` [3, 2]: **4 trials**; range 5 .. 60, stop 5 %, target 10 %.

## Ambiguities resolved

- Bull / bear power as written. Volume = broker tick volume (CVD). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_flow"`.

## Marks

`coarse_bar_stop`
