# #429956 基于Heikin-Ashi-ROC百分位数的交易策略Heikin-Ashi-ROC-Percentile-Trading-Strategy -> `fmz_429956_ha_roc_percentile`

- FMZ source id: 429956 (lineage).
- Source: https://www.fmz.com/strategy/429956 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-23 15:41:40). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Rates of change and their percentiles. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`roc_length` [100, 50] x `hl_len` [50, 25]: **4 trials**; percentiles 75 / 25 over 10 bars fixed.

## Ambiguities resolved

- Percentile convention stated. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
