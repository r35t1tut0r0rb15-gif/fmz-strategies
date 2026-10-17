# #434194 Adaptive Price Channel Strategy -> `fmz_434194_adx_switched_price_channel`

- FMZ source id: 434194 (lineage).
- Source: https://www.fmz.com/strategy/434194 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-04 16:33:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C65). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel distances in ATR and DI / ADX levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `atr_mult` [3.2, 1.5]: **4 trials**; ADX threshold 25 fixed.

## Ambiguities resolved

- The bar-count exit never fires, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
