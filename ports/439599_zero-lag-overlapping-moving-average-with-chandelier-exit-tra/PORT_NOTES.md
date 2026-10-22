# #439599 Zero Lag Overlapping Moving Average with Chandelier Exit Trading Strategy -> `fmz_439599_zlsma130_chandelier_flip_bracket`

- FMZ source id: 439599 (lineage).
- Source: https://www.fmz.com/strategy/439599 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-22 10:03:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C121). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed from the fill |
| 2 | PASS | Regression line side and Chandelier flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.02, 0.01] x `length1` [130, 50]: **4 trials**; stop 2 %, CE ATR 1 x 2 fixed.

## Ambiguities resolved

- Fixed 2 % bracket from the fill. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
