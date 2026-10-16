# #427992 Doji Candlestick Reversal Trading Strategy -> `fmz_427992_doji_reversal`

- FMZ source id: 427992 (lineage).
- Source: https://www.fmz.com/strategy/427992 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-27 16:40:28). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Candle ratios and MA length. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_period` [10, 20] x `tolerance` [0.1, 0.05]: **4 trials**; defaults 10 / 0.1 (the source's); look-back end fixed (no effect).

## Ambiguities resolved

- For i >= 2 the loop's conditions contradict, so only the previous bar's doji counts (as written).
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
