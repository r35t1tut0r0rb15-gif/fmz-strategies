# #429577 The Multi Timeframe Bottom Reversal Strategy -> `fmz_429577_noro_bottom_score_rsi`

- FMZ source id: 429577 (lineage).
- Source: https://www.fmz.com/strategy/429577 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-18 12:27:29). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Ratios, ATR-normalised indicators and RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`botsens` [3, 2] x `oversold` [35, 45]: **4 trials**; the components and SMA 25 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_vote"`.

## Marks

`none`
