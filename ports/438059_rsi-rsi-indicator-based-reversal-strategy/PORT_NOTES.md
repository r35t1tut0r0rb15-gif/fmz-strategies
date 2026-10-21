# #438059 基于RSI指标的多空反转策略RSI-Indicator-Based-Reversal-Strategy -> `fmz_438059_rsi_obos_divergence_bracket`

- FMZ source id: 438059 (lineage).
- Source: https://www.fmz.com/strategy/438059 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 16:47:07). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C109). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | RSI pivots and divergences |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lb` [5, 3] x `stop` [0.005, 0.01]: **4 trials**; pivot sides swept together; RSI 14, the 30-bar OB / OS tests and the 2 % target fixed.

## Ambiguities resolved

- Strict pivots; bracket fixed at the fill. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
