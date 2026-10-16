# #430169 Gradual Accumulation Breakout Trading Strategy -> `fmz_430169_wyckoff_range_crosses`

- FMZ source id: 430169 (lineage).
- Source: https://www.fmz.com/strategy/430169 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-25 17:34:41). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at the fill (rule 2). |
| 2 | PASS | Moving-average crosses and a percentage stop. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`accumulation` [32, 50] x `stop_pct` [10.0, 5.0]: **4 trials**; distribution 35, spring 10, upthrust 20 fixed.

## Ambiguities resolved

- Pending (not emitted as written): the stop re-issued at 10 % from each bar's close (a level that moves both ways);
  fixed at 10 % of the fill instead.
- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
