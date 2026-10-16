# #429967 Trend Reversal System -> `fmz_429967_oath_cci_pullback_bracket`

- FMZ source id: 429967 (lineage).
- Source: https://www.fmz.com/strategy/429967 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-23 17:18:28). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | ADAPT | The pip target -> an ATR multiple; the spread constant dropped. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital-based order size stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429967. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.04, 2.0] x `mult` [5.0, 3.0]: **4 trials**; EMA 21 / 55, CCI 20 and level 1 fixed.

## Ambiguities resolved

- Spread constant dropped; pip target as an ATR multiple. Mark coarse_bar_stop. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
