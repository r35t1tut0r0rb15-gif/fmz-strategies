# #442363 Breakout Trading System -> `fmz_442363_donchian20_breakout_lower_band_exit_long`

- FMZ source id: 442363 (lineage).
- Source: https://www.fmz.com/strategy/442363 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 14:02:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C154). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426895. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 55]: **2 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
