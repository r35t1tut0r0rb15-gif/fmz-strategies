# #458192 Bollinger Bands Breakout Quantitative Trading Strategy -> `fmz_458192_bb20_band_close_fade_reversal`

- FMZ source id: 458192 (lineage).
- Source: https://www.fmz.com/strategy/458192 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 16:55:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C203). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band fades |
| 3 | PASS | No exchange header. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5]: **4 trials**.

## Ambiguities resolved

- No bar size in the source (bar_size_pending). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`bar_size_pending`
