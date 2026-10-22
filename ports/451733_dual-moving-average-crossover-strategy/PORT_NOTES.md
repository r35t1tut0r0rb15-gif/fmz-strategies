# #451733 Dual Moving Average Crossover Strategy -> `fmz_451733_sma50_200_cross_from_flat_2pct_stop`

- FMZ source id: 451733 (lineage).
- Source: https://www.fmz.com/strategy/451733 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 15:48:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C187). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the signal-close stop as a fixed fraction |
| 2 | PASS | Golden / death crosses from flat |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`quick` [50, 20] x `slow` [200, 100] x `sl_pct` [0.02, 0.05]: **8 trials**.

## Ambiguities resolved

- Stop as a fraction of the fill. Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
