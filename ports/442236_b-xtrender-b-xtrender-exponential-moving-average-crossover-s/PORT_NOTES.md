# #442236 指数均线交叉B-Xtrender策略B-Xtrender-Exponential-Moving-Average-Crossover-Strategy -> `fmz_442236_b_xtrender_agreement_ema200_pct_trail`

- FMZ source id: 442236 (lineage).
- Source: https://www.fmz.com/strategy/442236 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-20 14:45:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C153). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated) |
| 2 | PASS | Xtrender agreement, EMA filter and percent trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [200, 100] x `trail_pct` [0.2, 0.1]: **4 trials**; the Xtrender lengths fixed.

## Ambiguities resolved

- Percent trail on closes as a house trail (stated). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop`
