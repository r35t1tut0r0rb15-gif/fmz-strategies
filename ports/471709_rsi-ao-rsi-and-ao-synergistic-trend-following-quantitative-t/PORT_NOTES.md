# #471709 RSI与AO协同趋势追踪型量化交易策略-RSI-and-AO-Synergistic-Trend-Following-Quantitative-Trading-Strategy -> `fmz_471709_negative_ao_after_rsi_over_50_pct_bracket_long`

- FMZ source id: 471709 (lineage).
- Source: https://www.fmz.com/strategy/471709 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 16:05:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C210). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price bracket as fixed fractions |
| 2 | PASS | Negative AO after RSI strength, percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.02, 0.04] x `sl_pct` [0.01, 0.02]: **4 trials**; the AO and RSI lengths fixed.

## Ambiguities resolved

- Bracket from the fill bar. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
