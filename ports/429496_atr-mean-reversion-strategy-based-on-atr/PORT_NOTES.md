# #429496 基于ATR的均值回复策略Mean-Reversion-Strategy-Based-on-ATR -> `fmz_429496_atr_divergence_drift_long`

- FMZ source id: 429496 (lineage).
- Source: https://www.fmz.com/strategy/429496 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-17 16:27:44). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated). |
| 2 | PASS | ATR ratios, log returns and an ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 1 stored; the trailing stop quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`z` [1.645, 1.96] x `trail_k` [2.0, 3.0]: **4 trials**; ATR 14 / 28, drift 14 fixed.

## Ambiguities resolved

- Trail anchor and latch reset approximated as stated. Long only. Marks coarse_bar_stop, trailing_stop.
- FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_spike_reversal"`.

## Marks

`coarse_bar_stop, trailing_stop`
