# #489285 智能交易动量均线混合策略-Smart-Trading-Momentum-and-Moving-Average-Hybrid-Strategy -> `fmz_489285_sma_13_5_cross_always_in`

- FMZ source id: 489285 (lineage).
- Source: https://www.fmz.com/strategy/489285 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 10:42:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving averages only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 3 %-risk quantity and the inert bracket quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [13, 20] x `slow` [5, 8]: **4 trials**; defaults 13 / 5 (the source's, "fast" being the longer SMA).

## Ambiguities resolved

- The exits' from_entry ("Long" / "Short") match no entry id (the entries are named in Hindi): inert, not emitted.
- Always in after the first cross. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
