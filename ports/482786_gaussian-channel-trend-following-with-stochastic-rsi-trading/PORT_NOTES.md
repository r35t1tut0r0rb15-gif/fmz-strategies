# #482786 Gaussian Channel Trend Following with Stochastic RSI Trading Strategy -> `fmz_482786_gauss20_weighted_channel_upper_break_stochrsi_long`

- FMZ source id: 482786 (lineage).
- Source: https://www.fmz.com/strategy/482786 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 11:01:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C249). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Gaussian channel breakouts with Stochastic RSI confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported; commission not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `multiplier` [2.0, 1.0]: **4 trials**; RSI 14, Stoch 14 / 3 / 3.

## Ambiguities resolved

- Centred Gaussian weights inside the trailing window, as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
