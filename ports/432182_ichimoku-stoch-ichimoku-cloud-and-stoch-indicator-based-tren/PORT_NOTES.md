# #432182 基于ICHIMOKU形态和STOCH指标的趋势跟踪策略ICHIMOKU-Cloud-and-STOCH-Indicator-Based-Trend-Tracking-Strategy -> `fmz_432182_ichimoku_trend_stoch_cross`

- FMZ source id: 432182 (lineage).
- Source: https://www.fmz.com/strategy/432182 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-15 11:19:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick distances -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the exits are ported via stops() and quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.6, 1.5] x `tp_atr` [0.9, 3.0]: **4 trials**; the stochastic, the Ichimoku lengths, the levels and ATR 14 fixed.

## Ambiguities resolved

- Level names swapped in the source, used as written. Tick bracket as ATR fractions. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
