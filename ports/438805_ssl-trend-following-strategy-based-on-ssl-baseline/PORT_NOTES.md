# #438805 基于SSL的均线趋势跟随策略Trend-Following-Strategy-Based-on-SSL-Baseline -> `fmz_438805_ssl_baseline_channel_atr_bracket`

- FMZ source id: 438805 (lineage).
- Source: https://www.fmz.com/strategy/438805 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-15 14:36:39). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C113). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Baseline channel and ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [30, 60] x `sl_mult` [4.0, 2.0]: **4 trials**; channel 0.2, ATR 14 and reward 2 fixed.

## Ambiguities resolved

- Entry flags cleared by the script's own level test. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
