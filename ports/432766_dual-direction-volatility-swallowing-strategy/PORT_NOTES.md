# #432766 Dual direction Volatility Swallowing Strategy -> `fmz_432766_volatility_stop_swing_long`

- FMZ source id: 432766 (lineage).
- Source: https://www.fmz.com/strategy/432766 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-21 12:04:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C53). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An ATR volatility stop crossed on the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, the commission and the direction setting stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG432766. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [3, 10] x `mult` [1.0, 2.0]: **4 trials**.

## Ambiguities resolved

- Short entries only close the long (allow_entry_in long). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
