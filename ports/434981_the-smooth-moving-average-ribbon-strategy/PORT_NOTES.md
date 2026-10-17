# #434981 The Smooth Moving Average Ribbon Strategy -> `fmz_434981_smooth_ha_ribbon`

- FMZ source id: 434981 (lineage).
- Source: https://www.fmz.com/strategy/434981 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-11 14:48:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C72). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed candle crosses and an average slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND431223. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [11, 21] x `ma_length` [100, 50]: **4 trials**; three EMA smoothings and both HA passes fixed.

## Ambiguities resolved

- First-bar HA seed as written; entry beats close_all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks

`none`
