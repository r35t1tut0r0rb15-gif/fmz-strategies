# #441991 基于双EMA指标的趋势跟随策略Dual-EMA-Indicator-Based-Trend-Following-Strategy -> `fmz_441991_ema34_89_cross_reversal`

- FMZ source id: 441991 (lineage).
- Source: https://www.fmz.com/strategy/441991 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-18 14:38:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C149). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG441991. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [34, 20] x `long_len` [89, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
