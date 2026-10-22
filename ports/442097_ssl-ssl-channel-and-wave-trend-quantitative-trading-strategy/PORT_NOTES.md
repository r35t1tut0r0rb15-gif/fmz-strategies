# #442097 基于SSL通道和波浪趋势的量化交易策略SSL-Channel-and-Wave-Trend-Quantitative-Trading-Strategy -> `fmz_442097_ssl_wavetrend_keltner_atr_bracket`

- FMZ source id: 442097 (lineage).
- Source: https://www.fmz.com/strategy/442097 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-19 11:47:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C150). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | PASS | SSL, Wave Trend, Keltner and EMA filters with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 1 % risk quantity, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr_mult` [1.7, 2.5] x `risk_reward` [2.5, 1.5]: **4 trials**; indicator lengths fixed.

## Ambiguities resolved

- Percent-of-close bracket re-based on the fill; entry-gate flags as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
