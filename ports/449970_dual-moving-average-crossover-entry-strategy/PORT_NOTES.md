# #449970 Dual Moving Average Crossover Entry Strategy -> `fmz_449970_open_above_sma5_breakeven_close_long`

- FMZ source id: 449970 (lineage).
- Source: https://www.fmz.com/strategy/449970 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 17:37:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C183). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the exit is a close test against the fill |
| 2 | PASS | Open above the SMA 5 with a break-even-or-better close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [5, 10]: **2 trials**.

## Ambiguities resolved

- Scenario 2 never fires. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
