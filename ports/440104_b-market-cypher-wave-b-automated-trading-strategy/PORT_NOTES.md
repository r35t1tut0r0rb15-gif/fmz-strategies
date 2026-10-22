# #440104 市场密码波浪B自动买卖策略Market-Cypher-Wave-B-Automated-Trading-Strategy -> `fmz_440104_wavetrend_extreme_cross`

- FMZ source id: 440104 (lineage).
- Source: https://www.fmz.com/strategy/440104 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-26 16:16:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C131). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the lookahead requests feed plots only |
| 2 | PASS | WaveTrend crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Initial capital and equity gate are sizing. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ob_level` [70, 53] x `avg_len` [12, 21]: **4 trials**; oversold = -overbought; channel 9 and signal 3 fixed.

## Ambiguities resolved

- Placeholder levels place nothing; plots and alerts not ported. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend_oscillator"`.

## Marks

`none`
