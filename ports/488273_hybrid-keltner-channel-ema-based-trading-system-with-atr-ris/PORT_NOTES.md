# #488273 尺度移动均线与双布林线动量混合交易系统-Hybrid-Keltner-Channel-EMA-Based-Trading-System-with-ATR-Risk-Management -> `fmz_488273_keltner_fade_ema_trend_bracket`

- FMZ source id: 488273 (lineage).
- Source: https://www.fmz.com/strategy/488273 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 14:21:48). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar (re-issue marked). |
| 2 | PASS | Channels, EMAs and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kc_mult` [1.5, 2.0] x `sl_mult` [1.5, 1.0]: **4 trials**; defaults 1.5 / 1.5 (the source's); target 2 x the stop,
KC / ATR length 20 and EMA 9 / 21 / 50 fixed.

## Trailing stop (mark `trailing_stop_pending`)

As written, `strategy.exit` for each entry id is re-issued every bar with the stop and target from the CURRENT close
and ATR (a moving bracket). The port fixes it at the signal bar (re-based on the fill).

## Ambiguities resolved

- Four entry ids, one position (pyramiding 1): a same-side entry under another id is ignored; an opposite entry
  reverses; entries on one bar in the order written. Each close applies only to the id that opened the position,
  from the position at the bar's start (#430850). `simulate()` mirrors the fixed bracket from the fill bar
  (#430254) to know which id holds the position. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
  FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "keltner_channel"`.

## Marks

`trailing_stop_pending`
