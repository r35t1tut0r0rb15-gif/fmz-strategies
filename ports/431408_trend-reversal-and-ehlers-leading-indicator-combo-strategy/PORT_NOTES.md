# #431408 Trend Reversal and Ehlers Leading Indicator Combo Strategy -> `fmz_431408_combo_123_daily_eli`

- FMZ source id: 431408 (lineage).
- Source: https://www.fmz.com/strategy/431408 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-07 16:10:26). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | A stochastic and an EMA difference |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `eli_len` [7, 14]: **4 trials**; K 1, D 3 and level 50 fixed.

## Ambiguities resolved

- Daily hl2 from completed broker days. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
