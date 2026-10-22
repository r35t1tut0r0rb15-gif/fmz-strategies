# #482779 基于KAMA与MACD的自适应趋势跟踪量化交易策略-Adaptive-Trend-Following-Strategy-Based-on-KAMA-and-MACD-Integration -> `fmz_482779_kama50_cross_macd26_52_side_long`

- FMZ source id: 482779 (lineage).
- Source: https://www.fmz.com/strategy/482779 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 15:01:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C249). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; re-sent ATR bracket described (pending) |
| 2 | PASS | KAMA crossings with a MACD side filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ama_length` [50, 20] x `slow_length` [30, 60]: **4 trials**; fast 3, MACD 26 / 52 / 18; the bracket is pending.

## Ambiguities resolved

- The re-sent 3 ATR bracket is pending. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`trailing_stop_pending`
