# #440005 基于CMO和WMA的双均线交易策略CMO-and-WMA-Based-Dual-Moving-Average-Trading-Strategy -> `fmz_440005_hpotter_cmo_wma_zone_state`

- FMZ source id: 440005 (lineage).
- Source: https://www.fmz.com/strategy/440005 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-25 17:44:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C129). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Momentum ratio zones |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430117. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [9, 14] x `buy_zone` [60.0, 40.0]: **4 trials**; sell zone = -buy zone, WMA 9 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
