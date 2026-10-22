# #440444 Trend Following Strategy Based on Adaptive Moving Average -> `fmz_440444_kama_slope_filter_long`

- FMZ source id: 440444 (lineage).
- Source: https://www.fmz.com/strategy/440444 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 16:30:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C134). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Adaptive average slope against its own deviation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length1` [14, 30] x `exit_filter` [0.5, 1.0]: **4 trials**; fast 2, slow 20 and entry filter 1 fixed.

## Ambiguities resolved

- KAMA from 0 as written; KAMA exit only. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
