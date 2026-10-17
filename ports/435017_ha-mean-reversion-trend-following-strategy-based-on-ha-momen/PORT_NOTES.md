# #435017 基于均线和HA动量突破的趋势跟踪策略Mean-Reversion-Trend-Following-Strategy-Based-on-HA-Momentum-Breakout -> `fmz_435017_body_momentum_trend_bracket`

- FMZ source id: 435017 (lineage).
- Source: https://www.fmz.com/strategy/435017 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-11 16:56:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C73). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick distances -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 2 % of equity stored; the tick bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`strength` [2.0, 1.5] x `sl_atr` [0.33, 1.0]: **4 trials**; the target is 3 x the stop (1500 / 500); SMA 20 / 200 and ATR 14 fixed.

## Ambiguities resolved

- Tick bracket -> ATR multiples. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
