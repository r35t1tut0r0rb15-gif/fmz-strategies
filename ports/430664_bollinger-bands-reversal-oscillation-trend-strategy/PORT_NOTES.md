# #430664 Bollinger Bands Reversal Oscillation Trend Strategy -> `fmz_430664_bb_breakout_sma_exit`

- FMZ source id: 430664 (lineage).
- Source: https://www.fmz.com/strategy/430664 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-31 14:30:45). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bollinger bands and a moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed-ratio cash sizing stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 50] x `mult` [2.0, 1.5]: **4 trials**; exit SMA 20 fixed.

## Ambiguities resolved

- Closes before entries (reversal stands). Fixed-ratio sizing not ported. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
