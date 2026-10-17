# #489742 八阶蜡烛模式序列马丁格尔策略-Eight-Candle-Pattern-Sequence-Martingale-Strategy -> `fmz_489742_eight_candle_sequence_always_in`

- FMZ source id: 489742 (lineage).
- Source: https://www.fmz.com/strategy/489742 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-08 10:53:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle colours only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The martingale bet quoted, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`GRID = {}`: **1 trial** (the rule as written; the source has no signal parameters).

## Ambiguities resolved

- The martingale (bet x 2 after a loss, capped at the capital limit) is sizing. A doji is neither colour.
- Always in after the first signal. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
