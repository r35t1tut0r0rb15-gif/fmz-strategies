# #442567 基于动量突破EMA交叉策略Momentum-Breakout-EMA-Crossover-Strategy -> `fmz_442567_ema9_21_cross_sma50_filter_reversal`

- FMZ source id: 442567 (lineage).
- Source: https://www.fmz.com/strategy/442567 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 18:06:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C158). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with an SMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; the SMA 50 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
