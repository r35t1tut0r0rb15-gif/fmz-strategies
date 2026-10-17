# #433948 基于频道和线性回归的Hull-MA摆荡策略Hull-MA-Channel-and-Linear-Regression-Swing-Trading-Strategy -> `fmz_433948_hull_sonicr_swing`

- FMZ source id: 433948 (lineage).
- Source: https://www.fmz.com/strategy/433948 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-01 16:47:01). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C64). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average and channel relations (the exit compares two price distances) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hull_len` [377, 200] x `ema_sig` [89, 55]: **4 trials**; channel 34 and regression 89 / 34 fixed.

## Ambiguities resolved

- Statement order kept for same-bar closes. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
