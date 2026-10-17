# #489016 自适应波动突破回撤交易策略-Adaptive-Volatility-Breakout-Retest-Trading-Strategy -> `fmz_489016_sma200_cross_retest_atr_bracket`

- FMZ source id: 489016 (lineage).
- Source: https://www.fmz.com/strategy/489016 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 10:54:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | An SMA and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`risk_factor` [1.0, 2.0] x `ma_len` [200, 100]: **4 trials**; defaults 1 / 200 (the source's); ATR 14 fixed.

## Ambiguities resolved

- The retest windows include the current bar. REVERSAL INTENDED. Broker-day bars; FREQ = "1D"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop`
