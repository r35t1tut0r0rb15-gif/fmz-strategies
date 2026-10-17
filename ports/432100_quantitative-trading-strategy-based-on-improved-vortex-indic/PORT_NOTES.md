# #432100 Quantitative Trading Strategy Based on Improved Vortex Indicator -> `fmz_432100_vortex_spread_threshold`

- FMZ source id: 432100 (lineage).
- Source: https://www.fmz.com/strategy/432100 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-14 14:40:54). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed percentage brackets |
| 2 | PASS | A vortex spread and percentage exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 10 % position size in the comments only; no sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [300, 100] x `thresh` [16.2, 8.0]: **4 trials**; EMA 7 and the brackets fixed.

## Ambiguities resolved

- close_all after an entry leaves the bar flat. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
