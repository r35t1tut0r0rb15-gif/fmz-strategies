# #428053 Rainbow Moving Average Trading Strategy -> `fmz_428053_rainbow_ma_rsi_filter`

- FMZ source id: 428053 (lineage).
- Source: https://www.fmz.com/strategy/428053 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 11:01:59). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths and RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1_len` [12, 24] x `dis_len` [3, 5]: **4 trials**; defaults 12 / 3 (the source's); RSI filters fixed.

## Ambiguities resolved

- RSI filter enabled, SMA type (defaults). The "filter" (colour change without a signal) closes both sides.
- Colour is "none" while any line is na. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
