# #440817 Open High Close Low Breakout Trading Strategy -> `fmz_440817_open_at_extreme_reversal`

- FMZ source id: 440817 (lineage).
- Source: https://www.fmz.com/strategy/440817 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-02 12:03:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C140). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Open at the bar's extreme |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Lot size is sizing. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG440817. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tol_frac` [0.0]: **1 trial**; the exact test as written; the author's inputs do not change the orders, so one trial.

## Ambiguities resolved

- na stop / target place nothing (default inputs). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
