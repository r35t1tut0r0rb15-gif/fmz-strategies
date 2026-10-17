# #435134 Rate of Change Quantitative Strategy -> `fmz_435134_roc365_bubble_stop_reverse`

- FMZ source id: 435134 (lineage).
- Source: https://www.fmz.com/strategy/435134 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-12 15:56:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C74). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry; re-entry tracked through the house stop |
| 2 | PASS | Rate-of-change levels and a percent stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed-ratio cash orders and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`roc_len` [365, 180] x `sl_pct` [0.10, 0.05]: **4 trials**; bubble 200 fixed.

## Ambiguities resolved

- Stop-and-reverse tracked through the house stop; last issued entry wins. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`coarse_bar_stop`
