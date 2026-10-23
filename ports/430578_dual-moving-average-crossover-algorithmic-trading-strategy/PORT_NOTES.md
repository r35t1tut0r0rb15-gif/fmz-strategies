# #430578 Dual Moving Average Crossover Algorithmic Trading Strategy -> `fmz_430578_vwap_mean_reversion_plus_vwap_lead_line_trend_long`

- FMZ source id: 430578 (lineage).
- Source: https://www.fmz.com/strategy/430578 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-30 15:27:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | VWAP mean reversion combined with a VWAP lead-line trend setup |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital 1000, commission 0.025 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`percent_below` [2.0, 1.0] x `rsi_level` [30.0, 20.0]: **4 trials**; the trend half as written.

## Ambiguities resolved

- One position, exit by the holding setup's rule. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_weighted_ma"`.

## Marks

`none`
