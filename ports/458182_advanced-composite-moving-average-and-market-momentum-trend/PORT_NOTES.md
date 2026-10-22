# #458182 Advanced Composite Moving Average and Market Momentum Trend Capture Strategy -> `fmz_458182_double_hull_turn_ichimoku_filters_reversal`

- FMZ source id: 458182 (lineage).
- Source: https://www.fmz.com/strategy/458182 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-07-30 16:27:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C203). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Hull-style turns with Ichimoku filters |
| 3 | PASS | No exchange header. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`keh` [12, 24] x `kijun` [24, 26]: **4 trials**; Tenkan 9, Span B 51 and the displacement 24 fixed.

## Ambiguities resolved

- No bar size in the source (bar_size_pending); call order followed. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`bar_size_pending`
