# #474710 Multi Factor Counter Trend Trading Strategy -> `fmz_474710_bar_counter_keltner_reversal_10m`

- FMZ source id: 474710 (lineage).
- Source: https://www.fmz.com/strategy/474710 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 17:36:41). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Counter-trend entries at Keltner Channel extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 80 % of equity, capital and commission stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`count` [3, 5] x `mult` [2, 3]: **4 trials**; KC 20.

## Ambiguities resolved

- Volume branch off by default. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "keltner_reversion"`.

## Marks

`none`
