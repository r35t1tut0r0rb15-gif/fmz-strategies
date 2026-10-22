# #440337 RSI鳄鱼趋势策略RSI-Alligator-Trend-Strategy -> `fmz_440337_rsi_alligator_long_bracket`

- FMZ source id: 440337 (lineage).
- Source: https://www.fmz.com/strategy/440337 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-29 14:40:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C132). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | RSI crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash size, capital, commission and slippage settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.10, 0.03] x `tp` [0.90, 0.10]: **4 trials**; RSI lengths 5 / 13 / 34 fixed.

## Ambiguities resolved

- Long Only type ported; date window not applied. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
