# #484924 多重技术指标黄金即时变动检测与风险管理策略-Multi-Technical-Indicator-Gold-Real-Time-Movement-Detection-and-Risk-Management-Strategy -> `fmz_484924_chandelier_flip_small_bracket`

- FMZ source id: 484924 (lineage).
- Source: https://www.fmz.com/strategy/484924 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-05 10:35:15). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | ADAPT | 3 / 5 price units -> 0.025 / 0.04 ATR; ATR channel. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.025, 1.0] x `ce_mult` [3.0, 2.0]: **4 trials**; defaults 0.025 / 3 (the source as written: on daily
ETH_USDT, ATR about 120, the 3-unit stop is about 0.025 ATR; judgement stated before any backtest); target 5 / 3 of
the stop, Chandelier length 22 (closes) and ATR 14 fixed.

## Ambiguities resolved

- With the confirmation filters off (defaults) and alternate signals on, the signal-expiry and CondIni logic reduce
  to: long on the bar the Chandelier direction turns up, short on the bar it turns down (the first run from the
  start sets the state without a trade). The signals alternate: no same-side re-placement.
- The MA lines (VWMA only as an option), SuperTrend, STC and dashboard are display or disabled. REVERSAL INTENDED.
  Stop module: `portfolio_kwargs` {} (D4). Daily bars are broker days; FREQ = "1D" ("1 Min Gold" is a label):
  `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "chandelier_exit"`.

## Marks

`coarse_bar_stop`
