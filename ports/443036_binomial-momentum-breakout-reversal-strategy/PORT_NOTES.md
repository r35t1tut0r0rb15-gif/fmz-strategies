# #443036 Binomial Momentum Breakout Reversal Strategy -> `fmz_443036_reversal123_bull_power_combo`

- FMZ source id: 443036 (lineage).
- Source: https://www.fmz.com/strategy/443036 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-28 17:20:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C165). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit levels -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430543. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `sell_frac` [3.57e-04, 0.002]: **4 trials**; the buy level fraction fixed.

## Ambiguities resolved

- Price-unit levels as fractions of the close. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
