# #449956 三重EMA交叉策略Triple-EMA-Crossover-Strategy -> `fmz_449956_triple_ema_cross_atr_bracket_reversal`

- FMZ source id: 449956 (lineage).
- Source: https://www.fmz.com/strategy/449956 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 16:34:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C182). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed on the signal bar (re-sent levels marked) |
| 2 | PASS | EMA crossings with a middle-EMA filter, ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 10 % of equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`risk_mult` [3.0, 1.5] x `slow` [50, 100]: **4 trials**; the 2 : 1 target ratio and the fast / middle EMAs fixed.

## Ambiguities resolved

- Levels from the signal bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
