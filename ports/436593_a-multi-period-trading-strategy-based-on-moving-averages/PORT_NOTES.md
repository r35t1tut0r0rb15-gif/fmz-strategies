# #436593 A Multi Period Trading Strategy Based on Moving Averages -> `fmz_436593_macd_bb_rsi_dip`

- FMZ source id: 436593 (lineage).
- Source: https://www.fmz.com/strategy/436593 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-26 10:13:34). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C92). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | REVIEW | Optional stop off by default |
| 2 | PASS | MACD crossing with band and RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the stop inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [12, 8] x `length` [20, 30]: **4 trials**; RSI 14, limits 50 / 70 and the band multiple 2 fixed.

## Ambiguities resolved

- Optional stop not ported. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_signal"`.

## Marks

`none`
