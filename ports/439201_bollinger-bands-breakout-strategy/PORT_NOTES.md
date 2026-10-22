# #439201 Bollinger Bands Breakout Strategy -> `fmz_439201_bb_band_close_reversal`

- FMZ source id: 439201 (lineage).
- Source: https://www.fmz.com/strategy/439201 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-18 12:18:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C117). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG439201. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `mult` [2.0, 3.0]: **4 trials**.

## Ambiguities resolved

- State entries beyond the bands. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
