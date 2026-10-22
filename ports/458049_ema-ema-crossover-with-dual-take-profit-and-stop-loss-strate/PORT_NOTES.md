# #458049 EMA交叉指示双重止盈止损策略-EMA-Crossover-with-Dual-Take-Profit-and-Stop-Loss-Strategy -> `fmz_458049_ema20_50_cross_ema50_anchored_stop_reversal`

- FMZ source id: 458049 (lineage).
- Source: https://www.fmz.com/strategy/458049 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 14:46:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C200). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the EMA-based stop and tick target as fractions of the signal close |
| 2 | PASS | EMA crossings with an EMA-anchored stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [20, 9] x `long_len` [50, 100] x `tp_atr` [0.05, 2.0]: **8 trials**; the 0.025 ATR stop offset fixed.

## Ambiguities resolved

- Ticks as ATR multiples (4h ~400). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
