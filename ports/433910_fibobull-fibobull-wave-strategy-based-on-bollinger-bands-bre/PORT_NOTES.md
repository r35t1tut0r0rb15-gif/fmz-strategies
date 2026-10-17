# #433910 基于布林带突破的FiboBuLL波浪策略FiboBuLL-Wave-Strategy-Based-on-Bollinger-Bands-Breakout -> `fmz_433910_fibobull_band_regime`

- FMZ source id: 433910 (lineage).
- Source: https://www.fmz.com/strategy/433910 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-01 14:11:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C63). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band breaks and their recency |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG433910. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 42] x `mult` [1.0, 2.0]: **4 trials**.

## Ambiguities resolved

- The wrong-id close does nothing, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
