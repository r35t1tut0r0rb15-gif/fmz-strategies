# #474958 Dual EMA Crossover Strategy with Smart Risk Reward Control -> `fmz_474958_ema15_50_cross_prev_opens_stop_2r_reversal`

- FMZ source id: 474958 (lineage).
- Source: https://www.fmz.com/strategy/474958 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 10:30:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C226). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | EMA crossings with a previous-opens stop and a 2 R target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [15, 10] x `long_len` [50, 100]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
