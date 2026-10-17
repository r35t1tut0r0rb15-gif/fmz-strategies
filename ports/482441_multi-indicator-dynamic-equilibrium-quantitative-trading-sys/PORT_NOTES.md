# #482441 多指标动态平衡量化交易系统-Multi-Indicator-Dynamic-Equilibrium-Quantitative-Trading-System -> `fmz_482441_rsi_bb_dip_or_ema_macd_trend_long`

- FMZ source id: 482441 (lineage).
- Source: https://www.fmz.com/strategy/482441 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 14:44:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI, Bollinger bands, EMAs and MACD. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 250 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [2.0, 1.5] x `ob` [70, 80]: **4 trials**; defaults 2 / 70 (the source's); RSI 14 (30), BB 20, EMA 50 / 200
and MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- The close acts on the position held at the bar's start and never undoes an entry on that bar (#430850).
- Long only. Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
