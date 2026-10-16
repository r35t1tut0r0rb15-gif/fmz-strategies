# #428790 A Momentum Breakout Strategy -> `fmz_428790_camarilla_h4_l4_breakout`

- FMZ source id: 428790 (lineage).
- Source: https://www.fmz.com/strategy/428790 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-09 15:15:22). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily levels from completed broker days. |
| 2 | PASS | Levels from the day's own range. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG428790, ND428790. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`frac` [0.5, 0.25] (the H4 / L4 and H3 / L3 Camarilla fractions of 1.1 x range): **2 trials**.

## Ambiguities resolved

- Daily values from the port's bars on broker days, the previous completed day. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
