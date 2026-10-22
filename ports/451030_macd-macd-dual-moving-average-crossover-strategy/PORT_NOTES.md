# #451030 MACD双均线交叉策略-MACD-Dual-Moving-Average-Crossover-Strategy -> `fmz_451030_macd_cross_prior_bar_stop_4r_reversal`

- FMZ source id: 451030 (lineage).
- Source: https://www.fmz.com/strategy/451030 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-05-11 12:00:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C184). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the long bracket fixed on the signal bar; the short's wrong-side target read as a close |
| 2 | PASS | MACD signal crossings with a prior-bar stop and a 4R target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [4.0, 2.0] x `fast` [12, 8]: **4 trials**; the slow and signal lengths fixed.

## Ambiguities resolved

- Shorts close at the next open after their fill (wrong-side target). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
