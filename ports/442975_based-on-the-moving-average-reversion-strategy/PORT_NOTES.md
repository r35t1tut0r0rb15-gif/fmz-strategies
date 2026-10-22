# #442975 Based on the Moving Average Reversion Strategy -> `fmz_442975_jaws_sma2_under_sma5_gap_long`

- FMZ source id: 442975 (lineage).
- Source: https://www.fmz.com/strategy/442975 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-27 17:51:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C164). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Short / long SMA gap |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`big` [5, 10] x `pct_below` [3.0, 5.0]: **4 trials**; the SMA 2 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
