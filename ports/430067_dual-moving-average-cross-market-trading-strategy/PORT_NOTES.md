# #430067 Dual Moving Average Cross Market Trading Strategy -> `fmz_430067_hull_t3_swing`

- FMZ source id: 430067 (lineage).
- Source: https://www.fmz.com/strategy/430067 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-24 16:55:38). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving exit levels fixed at the fill (rule 2). |
| 2 | PASS | Moving-average slopes and percentage exits. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the exit distances quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 30] x `tp_long` [0.08, 0.04]: **4 trials**; T3 factor 0.7, short TP 3 % / SL 6 % fixed.

## Ambiguities resolved

- Pending (not emitted as written): the TP / SL distances re-computed from each bar's close (moving levels); fixed at
  the fill instead. The 100 % long stop is unreachable: not emitted.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`trailing_stop_pending`
