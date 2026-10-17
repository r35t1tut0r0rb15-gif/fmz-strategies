# #431662 High Low Breakout for Quantitative Trading -> `fmz_431662_combo_123_prev_day_levels`

- FMZ source id: 431662 (lineage).
- Source: https://www.fmz.com/strategy/431662 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-10 11:09:28). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | A stochastic and previous-day levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND431662. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `level` [50, 40]: **4 trials**; K 1, D 3 and lookback 1 fixed.

## Ambiguities resolved

- Previous broker day's high / low. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
