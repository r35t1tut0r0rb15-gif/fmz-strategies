# #488907 动态RSI低高点背离趋势策略-Dynamic-RSI-Low-High-Point-Divergence-Trend-Strategy -> `fmz_488907_rsi_extreme_at_price_extreme`

- FMZ source id: 488907 (lineage).
- Source: https://www.fmz.com/strategy/488907 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-31 17:24:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Rolling extremes and an oscillator |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [10, 20] x `oversold` [30, 40]: **4 trials**; defaults 10 / 30 (the source's); RSI 14 and 70 fixed.

## Ambiguities resolved

- Windows include the current bar. Always in after the first signal. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
