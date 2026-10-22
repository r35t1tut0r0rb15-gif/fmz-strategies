# #484771 Dual Moving Average Crossover with Trading Window and Risk Management Strategy -> `fmz_484771_sma10_25_cross_utc_half_hour_window_tick_bracket_reversal`

- FMZ source id: 484771 (lineage).
- Source: https://www.fmz.com/strategy/484771 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-04 10:59:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C262). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; tick bracket as fractions of the fill |
| 2 | ADAPT | 50 ticks read as a fraction at SOL 160 |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Quantity 2 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [10, 5] x `slow_length` [25, 50]: **4 trials**; bracket 3.125e-03 each side.

## Ambiguities resolved

- The window keeps the source's minute >= 30 test; the short's same-side bracket closes it next bar, as written.
- MPL 2.0 source, ported and stated. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
