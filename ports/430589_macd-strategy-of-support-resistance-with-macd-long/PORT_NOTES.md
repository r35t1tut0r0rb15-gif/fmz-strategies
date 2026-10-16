# #430589 支撑阻力与MACD长线策略Strategy-of-Support-Resistance-with-MACD-LONG -> `fmz_430589_macd_26_100_bracket_long`

- FMZ source id: 430589 (lineage).
- Source: https://www.fmz.com/strategy/430589 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-30 16:18:34). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (re-issues on later signals approximated). |
| 2 | PASS | MACD and percentage exits. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [100, 50] x `sl_pct` [5.0, 3.0]: **4 trials**; fast 26, signal 9, target 7.5 % fixed.

## Ambiguities resolved

- Pending (approximated): a cross while long re-issues the bracket at new levels in the source; the entry's bracket is kept.
- The always-true support filter is not ported. Mark coarse_bar_stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
