# #431415 Chaotic Trading Rules Stop Loss Strategy -> `fmz_431415_rsi_leverage_call`

- FMZ source id: 431415 (lineage).
- Source: https://www.fmz.com/strategy/431415 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-07 16:44:31). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits |
| 2 | ADAPT | Price-unit distances (the template's off values) not ported; leverage call as a fraction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The leverage input stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND431415. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`leverage` [200, 50] x `length` [14, 7]: **4 trials**; levels 30 / 70 fixed.

## Ambiguities resolved

- The 99999 price-unit exits are not ported (criterion 2); the call exits are. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
