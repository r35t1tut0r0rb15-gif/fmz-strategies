# #432235 Mean Reversion Momentum Strategy -> `fmz_432235_linreg_zscore_fade`

- FMZ source id: 432235 (lineage).
- Source: https://www.fmz.com/strategy/432235 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-15 17:40:59). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C50). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (the drift pending) |
| 2 | PASS | A regression z-score, SMA levels and percentage exits of the fill |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [10, 20] x `thr` [1.0, 2.0]: **4 trials**; MA exit 10, SMA 200 and the 1 % bracket fixed.

## Ambiguities resolved

- The bracket re-sized every bar is kept at 1 % of the fill (pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks

`trailing_stop_pending`
