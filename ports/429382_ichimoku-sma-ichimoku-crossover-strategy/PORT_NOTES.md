# #429382 均线Ichimoku交叉策略SMA-Ichimoku-Crossover-Strategy -> `fmz_429382_ichimoku_sma_ohlc4`

- FMZ source id: 429382 (lineage).
- Source: https://www.fmz.com/strategy/429382 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-16 15:46:38). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders (the intrabar settings are in a commented-out line). |
| 2 | PASS | Comparisons of averages and lines from the bars only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_long` [21, 30] x `sma_short` [19, 10]: **4 trials**; Ichimoku 9 / 26 / 52 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
