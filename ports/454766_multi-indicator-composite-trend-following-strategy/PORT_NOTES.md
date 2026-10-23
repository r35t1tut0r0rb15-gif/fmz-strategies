# #454766 Multi Indicator Composite Trend Following Strategy -> `fmz_454766_ema9_21_cross_debug_reversal`

- FMZ source id: 454766 (lineage).
- Source: https://www.fmz.com/strategy/454766 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 18:12:28). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA 9 / 21 crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**.

## Ambiguities resolved

- Only the EMA crossings trade. Volume not used. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
