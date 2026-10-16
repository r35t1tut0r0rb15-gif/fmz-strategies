# #428699 Parabolic SAR RSI Reversal Strategy -> `fmz_428699_sar_close_flip`

- FMZ source id: 428699 (lineage).
- Source: https://www.fmz.com/strategy/428699 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-08 14:21:17). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders (the intrabar settings are in a commented-out line). |
| 2 | PASS | SAR acceleration factors are dimensionless. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() line (100 % of equity, commission, capital) stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sar_start` [0.007, 0.02] x `sar_max` [0.24, 0.2]: **4 trials**; increment 0.017 fixed.

## Ambiguities resolved

- The commented-out strategy() settings are inert; the commented RSI exits are not ported.
- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
