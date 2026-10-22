# #475637 多重均线协同趋势波动交易策略基于ATR动态风控-Multi-EMA-Trend-Following-Swing-Trading-Strategy-with-ATR-Based-Risk-Management -> `fmz_475637_close_cross_ema20_ema50_side_atr_bracket_reversal`

- FMZ source id: 475637 (lineage).
- Source: https://www.fmz.com/strategy/475637 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-20 17:06:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C229). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Contract count stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [1.5, 3.0] x `ema_mid` [50, 100]: **4 trials**; EMA 20, ATR 14.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
