# #440829 Gold Cross Dead Cross Quantitative Trading Strategy -> `fmz_440829_sma30_200_cross_unit_bracket`

- FMZ source id: 440829 (lineage).
- Source: https://www.fmz.com/strategy/440829 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-02 14:46:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C140). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Price-unit bracket -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG440829. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`br_frac` [0.00095, 0.02] x `fast` [30, 50]: **4 trials**; SMA 200 fixed.

## Ambiguities resolved

- Price-unit bracket as fractions. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
