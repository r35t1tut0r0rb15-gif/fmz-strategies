# #426619 Trend Following Strategy Based on Triple Indicator Cloud Pattern -> `fmz_426619_hkst_cloud_long`

- Source: https://www.fmz.com/strategy/426619 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-13 17:38:55). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kaufman_len` [10, 20] x `hull_len` [20, 40] x `atr_factor` [2.0, 3.0]: **8 trials**, defaults 20 / 20 / 2 (the source's); ATR period 5 fixed.

## Ambiguities resolved

- The AMA starts from 0 (nz), so early values depend on the data start (decision owed, as #366388 / #370711).
- While the noise sum is na the efficiency ratio is 0 (na != 0 is false).
- `strategy.close("Up", shortCondition)`: second argument read as `when`.
- Long only. Daily bars are broker days.

- Same bar: from flat an entry stands; while long the close goes flat (Pine order).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`
