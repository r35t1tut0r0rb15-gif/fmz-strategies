# #442837 Four DEMA Multi Timeframe Trend Strategy -> `fmz_442837_four_dema_order_cross_exit_reversal`

- FMZ source id: 442837 (lineage).
- Source: https://www.fmz.com/strategy/442837 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-26 14:14:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C161). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | DEMA ordering with a cross exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short` [10, 5] x `long3` [30, 50]: **4 trials**; the DEMA 15 / 21 fixed.

## Ambiguities resolved

- cross() in either direction closes. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
