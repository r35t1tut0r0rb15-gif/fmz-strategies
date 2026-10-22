# #488889 5分钟K线KDJ指标动态响应交易策略-5-Minute-KDJ-Indicator-Dynamic-Response-Trading-Strategy -> `fmz_488889_stoch5_k_extremes_entries_exits_reversal`

- FMZ source id: 488889 (lineage).
- Source: https://www.fmz.com/strategy/488889 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-31 16:26:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C267). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic extremes as entries and exits |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Equity-sized quantity and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 14] x `long_entry` [5, 20]: **4 trials** (short entry 100 minus it); exits 90 / 10.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic"`.

## Marks

`none`
