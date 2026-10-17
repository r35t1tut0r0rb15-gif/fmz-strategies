# #490805 移动平均与动量蜡烛趋势跟踪系统-Moving-Average-and-Momentum-Candle-Trend-Following-System -> `fmz_490805_sma200_momentum_candle_bracket`

- FMZ source id: 490805 (lineage).
- Source: https://www.fmz.com/strategy/490805 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-16 16:01:57). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | ADAPT | 50 / 100 pips -> `sl_atr` / `tp_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.5, 1.0] x `tp_atr` [1.0, 2.0]: **4 trials**; defaults 0.5 / 1.0; SMA 200 fixed. On the source's daily
TRX_USD (tick 0.00001 at about 0.24) 50 / 100 pips are about 2 % / 4 %, about 0.5 / 1 daily ATR (judgement, stated
before any backtest).

## Ambiguities resolved

- Entries only with no open trade: simulate() follows the house bracket on bars (flat after the bar that reaches the
  stop or the target, from the fill bar). Opposite entries cannot occur.
- Broker-day bars; FREQ = "1D"; stops on daily bars: `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop`
