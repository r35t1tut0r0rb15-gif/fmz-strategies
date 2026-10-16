# #427440 Bollinger Breakout Strategy -> `fmz_427440_noro_bollinger_fade`

- FMZ source id: 427440 (lineage).
- Source: https://www.fmz.com/strategy/427440 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-21 10:38:13). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bands in standard deviations, candle colours. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, pyramiding 5 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40, 10] x `mult` [1, 2]: **6 trials**; defaults 20 / 1.0 (the source's).

## Ambiguities resolved

- Adds (pyramiding 5) are sizing; the year window is dropped.
- Entry before close_all on one bar (REVERSAL INTENDED). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
