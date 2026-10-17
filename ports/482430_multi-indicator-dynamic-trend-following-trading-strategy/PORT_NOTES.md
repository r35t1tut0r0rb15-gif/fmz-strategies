# #482430 多重指标动态跟踪趋势波段交易策略-Multi-Indicator-Dynamic-Trend-Following-Trading-Strategy -> `fmz_482430_ema50_cross_rsi_move_adx_atr_bracket`

- FMZ source id: 482430 (lineage).
- Source: https://www.fmz.com/strategy/482430 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 14:02:44). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | An EMA, RSI, a move-based ADX and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital-percent sizing and 15x leverage quoted; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [2.5, 1.5] x `tp_mult` [1.5, 3.0]: **4 trials**; defaults 2.5 / 1.5 (the source's); EMA 50, RSI 14 and the
move-based ADX 14 > 20 fixed.

## Ambiguities resolved

- The "ADX" uses raw up / down moves without a true range (as written).
- `trail_points` without `trail_offset` is inert; the timeout input is never used.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
