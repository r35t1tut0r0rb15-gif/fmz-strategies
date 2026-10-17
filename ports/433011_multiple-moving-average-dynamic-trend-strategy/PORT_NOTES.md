# #433011 Multiple Moving Average Dynamic Trend Strategy -> `fmz_433011_ott_var_percent_cross`

- FMZ source id: 433011 (lineage).
- Source: https://www.fmz.com/strategy/433011 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-23 15:40:15). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C57). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A percent band around an average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND361567. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [2, 5] x `percent` [1.4, 3.0]: **4 trials**; MA type VAR and CMO 9 fixed.

## Ambiguities resolved

- Percent band as written (not lane A's ATR band). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
