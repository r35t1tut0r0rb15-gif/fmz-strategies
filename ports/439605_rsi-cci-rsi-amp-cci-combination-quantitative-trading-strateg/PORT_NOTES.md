# #439605 RSI指标结合CCI指标的量化交易策略RSI-amp-CCI-Combination-Quantitative-Trading-Strategy -> `fmz_439605_macd_sign_cci_level_state`

- FMZ source id: 439605 (lineage).
- Source: https://www.fmz.com/strategy/439605 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-22 10:33:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C121). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | CCI levels and the MACD sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `fast_length` [12, 8]: **4 trials**; slow 26 fixed.

## Ambiguities resolved

- Precedence as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
