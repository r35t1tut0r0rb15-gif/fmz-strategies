# #430174 EMA交叉追踪策略EMA-Crossover-tracking-Strategy -> `fmz_430174_close_supertrend_ema_filter`

- FMZ source id: 430174 (lineage).
- Source: https://www.fmz.com/strategy/430174 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-25 17:44:35). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR bands and moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [11, 20] x `multiplier` [3.0, 2.0]: **4 trials**; EMA 20 / 50 fixed.

## Ambiguities resolved

- Trend flip closes; with the other side's EMA condition it reverses. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
