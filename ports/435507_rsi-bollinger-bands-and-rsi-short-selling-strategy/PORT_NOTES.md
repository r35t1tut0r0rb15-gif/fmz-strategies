# #435507 布林带和RSI短线策略Bollinger-Bands-and-RSI-Short-Selling-Strategy -> `fmz_435507_bollinger_rsi_short`

- FMZ source id: 435507 (lineage).
- Source: https://www.fmz.com/strategy/435507 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-15 15:54:05). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C79). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Exit levels swapped: exit signal as written |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, commission and the percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `mult` [2.0, 2.5]: **4 trials**; RSI 14 and the 70 level fixed.

## Ambiguities resolved

- Swapped exit levels act as an exit signal; bracket owed. Short only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
