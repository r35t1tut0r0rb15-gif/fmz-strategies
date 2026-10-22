# #440847 基于EMA和隐藏背离的趋势追踪策略EMA-RSI-Hidden-Divergence-Trend-Following-Strategy -> `fmz_440847_rsi_hidden_divergence_ema_trend_long`

- FMZ source id: 440847 (lineage).
- Source: https://www.fmz.com/strategy/440847 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-02 16:54:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C141). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | PASS | EMA trend, stochastic cross and RSI hidden divergence |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent of equity and capital settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`profitfactor` [1.6, 2.5] x `lo_len` [38, 20]: **4 trials**; the pivot and oscillator settings fixed.

## Ambiguities resolved

- Stop from the 38-bar low up to the signal bar, re-based on the fill. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
