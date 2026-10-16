# #430761 CCI Mean Reversion Channel Strategy -> `fmz_430761_cci_zero_sign`

- FMZ source id: 430761 (lineage).
- Source: https://www.fmz.com/strategy/430761 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-01 16:20:45). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | The sign of a CCI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10,000 cash per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50, 100]: **3 trials**.

## Ambiguities resolved

- Default zero-line mode only. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
