# #474977 Bollinger Bands Momentum Breakout Adaptive Trend Following Strategy -> `fmz_474977_bb20_upper_break_lower_exit_long`

- FMZ source id: 474977 (lineage).
- Source: https://www.fmz.com/strategy/474977 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 11:43:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C227). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band breakouts with an opposite-band exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size, commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 1.5]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
