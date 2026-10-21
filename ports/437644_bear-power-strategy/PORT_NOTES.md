# #437644 Bear Power Strategy -> `fmz_437644_bear_power_level_state`

- FMZ source id: 437644 (lineage).
- Source: https://www.fmz.com/strategy/437644 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-04 15:13:16). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C103). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit levels -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND437644. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sell_frac` [0.00024, 0.005]: **2 trials**; buy fraction = sell / 10; reverse off.

## Ambiguities resolved

- Price-unit levels -> fractions of the close. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
