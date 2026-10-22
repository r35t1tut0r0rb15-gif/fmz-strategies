# #458142 改进型双重-EMA-回撤突破交易策略-Enhanced-Dual-EMA-Pullback-Breakout-Trading-Strategy -> `fmz_458142_ema8_swing_pullback_breakout_pullback_no_exit_long`

- FMZ source id: 458142 (lineage).
- Source: https://www.fmz.com/strategy/458142 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 12:04:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C202). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Swing-high pullback and breakout set-ups |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [8, 21]: **2 trials**.

## Ambiguities resolved

- No exit (as written). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`none`
