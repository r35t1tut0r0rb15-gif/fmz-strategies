# #439244 双重EMA与RSI结合的趋势跟踪策略Dual-EMA-and-RSI-Combined-Trend-Tracking-Strategy -> `fmz_439244_ema200_rsi_pullback_atr_bracket`

- FMZ source id: 439244 (lineage).
- Source: https://www.fmz.com/strategy/439244 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-18 15:51:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C119). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | EMA trend, RSI crossings and ATR distances |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk percent, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [4.0, 2.0] x `risk_reward` [2.0, 1.0]: **4 trials**; EMA 200, RSI 10 at 40 / 60 and ATR 14 fixed.

## Ambiguities resolved

- Bracket from the signal bar's ATR. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
