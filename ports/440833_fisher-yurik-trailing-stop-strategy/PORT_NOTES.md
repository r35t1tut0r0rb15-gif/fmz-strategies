# #440833 Fisher Yurik Trailing Stop Strategy -> `fmz_440833_fisher_yurik_rise_trail_exit`

- FMZ source id: 440833 (lineage).
- Source: https://www.fmz.com/strategy/440833 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-02 14:57:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C140). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated) |
| 2 | ADAPT | Tick trail -> house trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [2, 10] x `activate` [0.071, 0.03]: **4 trials**; trail 2e-7 fixed.

## Ambiguities resolved

- Trail activation from the fill (the script anchors it on the signal close). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`trailing_stop, coarse_bar_stop`
