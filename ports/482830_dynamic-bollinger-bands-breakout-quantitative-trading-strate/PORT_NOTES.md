# #482830 Dynamic Bollinger Bands Breakout Quantitative Trading Strategy -> `fmz_482830_bb20_2_upper_break_lower_exit_long`

- FMZ source id: 482830 (lineage).
- Source: https://www.fmz.com/strategy/482830 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 14:51:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C250). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 1.5]: **4 trials**; basis SMA.

## Ambiguities resolved

- Basis menu default SMA. Long only. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
