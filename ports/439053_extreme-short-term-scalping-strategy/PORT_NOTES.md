# #439053 Extreme Short term Scalping Strategy -> `fmz_439053_linreg_band_scalp_tick_bracket`

- FMZ source id: 439053 (lineage).
- Source: https://www.fmz.com/strategy/439053 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-17 12:06:39). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C115). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick gap and bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_sl` [0.02, 0.5] x `k_gap` [0.02, 0.5]: **4 trials**; linreg 14 / offset 1, ATR 14 and the 3:1 target fixed.

## Ambiguities resolved

- Tick gap and bracket -> ATR multiples (reading and wider values). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop`
