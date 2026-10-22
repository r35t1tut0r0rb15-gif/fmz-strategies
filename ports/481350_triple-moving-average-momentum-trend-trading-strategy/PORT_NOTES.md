# #481350 Triple Moving Average Momentum Trend Trading Strategy -> `fmz_481350_sma20_50_cross_sma200_side_reversal_bracket`

- FMZ source id: 481350 (lineage).
- Source: https://www.fmz.com/strategy/481350 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 14:37:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C242). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the replaced position's price as the bracket base, as written |
| 2 | PASS | SMA crossings on the SMA 200 side with crossing closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin 100 % stored, not ported; the bracket percentages stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**; SMA 200, stop 2 %, target 4 %.

## Ambiguities resolved

- The bracket exists only on a reversal (from the replaced position's price), and the short's levels are on the wrong side, as written.
- REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
