# #428719 Momentum Trend Continuation Factor Strategy -> `fmz_428719_trend_continuation_factor`

- FMZ source id: 428719 (lineage).
- Source: https://www.fmz.com/strategy/428719 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-08 16:15:34). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A comparison of two sums in the same units. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [35, 20, 50]: **3 trials**; reverse false fixed.

## Ambiguities resolved

- The first bar's change is na: plus and minus are 0 there (iff with na). REVERSAL INTENDED.
- FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
