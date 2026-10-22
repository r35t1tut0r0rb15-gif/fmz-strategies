# #444350 基于超级趋势和MACD的风险控制策略Samsuga-SuperTrend-MACD-Strategy -> `fmz_444350_supertrend_flip_30m_macd_hist_reversal`

- FMZ source id: 444350 (lineage).
- Source: https://www.fmz.com/strategy/444350 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-11 11:24:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C170). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 30-minute values end with the hourly bar |
| 2 | PASS | SuperTrend flips with a MACD histogram filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [1.0, 3.0] x `atr_period` [7, 14]: **4 trials**; the MACD lengths fixed.

## Ambiguities resolved

- 30-minute histogram from the hour's last 30-minute bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
